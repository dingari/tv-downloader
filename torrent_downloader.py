import codecs, configparser, feedparser, os, re, time

from file_utils import FileUtils
from opensubtitles_api import OpenSubtitlesClient
from subprocess import Popen
from tl_scraper import TlClient
from tvdb_api import TvdbClient
from tvshows import TvShowUtils
from urllib.request import urlretrieve

RSS_INTERVAL = 15 * 60;
SCRAPE_INTERVAL = 15 * 60;
EXTRACT_INTERVAL = 15 * 60;

class TorrentDownloader:

    filters = [];

    def __init__(self, configfile, filterfile):
        config = configparser.ConfigParser();
        config.read_file(codecs.open(configfile, 'r', 'utf8'));

        # Torrent-related config
        self.feed_url = config['RSS'].get('rss_feed');
        self.torrent_client = config['Download'].get('client_path');
        self.download_folder = config['Download'].get('download_destination');

        tl_username = config['TL_Credentials'].get('username');
        tl_password = config['TL_Credentials'].get('password');
        self.tl_client = TlClient(tl_username, tl_password);

        # Rar-related config
        rartool_path = config['Extract'].get('tool_path');
        self.dest_basefolder = config['Extract'].get('extract_destination');
        self.extensions = config['Extract'].get('extensions');
        file_utils = FileUtils(rartool_path);

        # TVDB-related config
        tvdb_username = config['TVDB_Credentials'].get('username');
        tvdb_userkey = config['TVDB_Credentials'].get('userkey');
        tvdb_apikey = config['TVDB_Credentials'].get('apikey');
        self.tvdb_client = TvdbClient(tvdb_username, tvdb_userkey, tvdb_apikey);

        # Opensubtitles-related config
        os_username = config['OS_Credentials'].get('username');
        os_password = config['OS_Credentials'].get('password');
        os_useragent = config['OS_Credentials'].get('useragent');

        self.os_client = OpenSubtitlesClient(os_username, os_password, os_useragent);

        # Read filter config file
        config = configparser.ConfigParser(); # unneccessary?
        config.read_file(codecs.open(filterfile, 'r', 'utf8'));

        # Build filter list
        for section in config.sections():
            filt = [];
            name = config[section].get('name');
            quality = config[section].get('quality');
            self.filters.append(TvShowUtils.make_filter(name, quality=quality));

    def init_download(self, url):
        print('Downloading from:', url);

        path = url if re.match('.*/rss/.*', url) else self.tl_client.get_torrent(url);

        Popen([self.torrent_client, '/DIRECTORY', self.download_folder, path]);

    def batch_download(self, torrentlist):
        for entry in torrentlist:
            if(not TvShowUtils.is_downloaded(self.download_folder, entry)):
                init_download(entry.get('link'));

    def batch_extract(self):
        files = os.listdir(self.download_folder);

        for f in files:
            try:
                info = TvShowUtils.get_info(f);
            except ValueError:
                print('Illegal name: {}, skipping'.format(f));
                continue;

            name = info['name'];        
            season_str = 'Season ' + str(int(info['season']));

            if(TvShowUtils.is_extracted(self.dest_basefolder, info)):
                # print(info['name'], 'Season', info['season'], 'Episode', info['episode'], 'already exists, skipping');
                continue;

            dest_filename = None;
            try:
                episode_name = self.tvdb_client.get_episode_name(info);

                # Format filename properly, like: "Foobar - 603 - Foo Bar Baz Foo"
                dest_filename = '{} - {}{:02d} - {}'.format(name, info['season'], info['episode'], episode_name);
            except Exception as e:
                print('Error getting name for: {}, reason: {}'.format(info, e));

            src = os.path.join(self.download_folder, f);
            dest = os.path.join(self.dest_basefolder, name, season_str);

            # If we find a single file, copy it
            if(os.path.isfile(src)):
                copy_file(src, dest, dest_filename);
            else:
                # It's a directory
                # Look for .rar files there within and try to extract
                try:
                    extract_file(src, dest, dest_filename);            
                except rarfile.Error as re:
                    print('Error extracting: {}'.format(re));
                    # If extraction fails, look for a single file within the directory
                    # and copy it, if one is found
                    local_files = os.listdir(src);
                    matched_files = (f for f in local_files if re.match(self.extensions, f));

                    try:
                        filename = next(matched_files);
                        copy_file(os.path.join(src, filename), dest);
                        get_subtitles(os.path.join(dest, filename)); 
                    except:
                        # We're out of luck with this one
                        print('An unknown error occured while processing {}, skipping...'.format(src));
                        continue;

            # At last get subtitles for the downloaded episode
            # TODO: maybe leave this as a configurable option?
            try:   
                get_subtitles(os.path.join(dest, dest_filename));
            except FileNotFoundError as fe:
                print('{}'.format(fe));

    # filepath: Full path to file w/o extension
    #
    # Throws: FileNotFoundError if filepath does not yield
    #         a file during a scan for extensions
    def get_subtitles(self, filepath):
        # Destination folder, episode filename
        dest, filename = os.path.split(filepath);

        try:
            localfiles = os.listdir(dest);
            matched_files = (f for f in localfiles if re.match(filename + '\..*', f));
            (ext, ) = re.search('.*\.(.*)$', next(matched_files)).groups();
            filepath = os.path.join(dest, '{}.{}'.format(filename, ext));
        except StopIteration:
            raise FileNotFoundError('Can\'t get subtitles for non-existent file \'{}\''.format(filepath));

        try:
            print('Getting subtitles for', filepath);
            dl_link = self.os_client.get_subtitle_link(filepath);
            dl_file_path, headers = urlretrieve(dl_link);

            with ZipFile(dl_file_path, 'r') as zf:
                subfiles = (f for f in zf.namelist() if re.match('.*\.srt', f));
                subfile_name = next(subfiles);
                subfile_path = zf.extract(subfile_name, dest);

                # Destination filename without extension
                # (name, ) = re.search('(.*)\..*', filename).groups();

                # Only working with srt as of now, may need to think about
                # other formats as well
                new_subfile_path = os.path.join(dest, filename + '.srt');
                os.rename(subfile_path, new_subfile_path);
        except StopIteration:
            FileNotFoundError('No subtitle file found in downloaded archive');
        except IndexError:
            FileNotFoundError('No subtitles found');


    def filter_data(self, entries):
        result = [];

        if(entries is not None and self.filters is not None):
            for entry in entries:
                for filt in self.filters:
                    if(re.search(filt, entry['title'], re.IGNORECASE) is not None):
                        try:
                            info = TvShowUtils.get_info(entry['title']);
                            if(not TvShowUtils.is_contained(result, info)):
                                info['link'] = entry['link'];
                                result.append(info);
                        except Exception as e:
                            print('Error:', e);

        return result;

    def loop_forever(self):
        self.last_rss_update = 0;
        self.last_scrape = 0;
        self.last_batch_extract = 0;
        
        while(True):
            print("looping");
            now = time.time();

            if(now - self.last_rss_update > RSS_INTERVAL):
                print('Updating...');
                data = feedparser.parse(self.feed_url);
                self.last_rss_update = time.time();

            if(now - self.last_scrape > SCRAPE_INTERVAL):
                print('Scraping...');
                scraped_torrents = self.tl_client.scrape_torrents(max_pages=10);
                print('Found {} torrents since last scrape'.format(len(scraped_torrents)));
                data.entries.extend(scraped_torrents);
                self.last_scrape = time.time();

            self.batch_download(self.filter_data(data.entries));

            if(now - self.last_batch_extract):
                print('Performing batch extract...');
                self.batch_extract();
                self.last_batch_extract = time.time();

            sleep_interval = min(RSS_INTERVAL, SCRAPE_INTERVAL, EXTRACT_INTERVAL);
            print('Sleeping for', sleep_interval, 'seconds');
            time.sleep(sleep_interval); 