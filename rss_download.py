import codecs
import configparser
import feedparser
import os
import rarfile
import re
import shutil
import sys
import time
import tvshows

from subprocess import Popen
from tl_scraper import get_torrent_with_login, scrape_torrents
from urllib.request import urlretrieve
from zipfile import ZipFile

# Globals
feed_url = '';
client_path = '';
download_folder = '';

extract_tool_path = '';
extract_folder = '';
extensions = '';

matches = [];
filters = [];

RSS_INTERVAL = 15 * 60;
SCRAPE_INTERVAL = 15 * 60;
EXTRACT_INTERVAL = 15 * 60;

def init():
    print('init')
    
    # Read general config file
    global feed_url;
    global client_path;
    global download_folder;

    global extract_tool_path;
    global extract_folder;
    global extensions;
    
    config = configparser.ConfigParser();
    config.read_file(codecs.open('config.ini', 'r', 'utf8'));

    feed_url = config['RSS'].get('rss_feed');
    client_path = config['Download'].get('client_path');
    download_folder = config['Download'].get('download_destination');

    extract_tool_path = config['Extract'].get('tool_path');
    extract_folder = config['Extract'].get('extract_destination');
    extensions = config['Extract'].get('extensions');
    rarfile.UNRAR_TOOL = extract_tool_path;

    # Read filter config file
    config = configparser.ConfigParser(); # unneccessary?
    config.read_file(codecs.open('filters.ini', 'r', 'utf8'));

    # Build filter list
    for section in config.sections():
        filt = [];
        name = config[section].get('name');
        quality = config[section].get('quality');
        filters.append(tvshows.make_filter(name, quality=quality));

def init_download(url):
    print('Downloading from:', url);

    path = url if re.match('.*/rss/.*', url) else get_torrent_with_login(url);

    Popen([client_path, '/DIRECTORY', download_folder, path]);

def batch_download(matched_list):
    for entry in matched_list:
        if(not tvshows.is_downloaded(download_folder, entry)):
            init_download(entry.get('link'));

def batch_extract():
    files = os.listdir(download_folder);

    for f in files:
        try:
            info = tvshows.get_info(f);
        except ValueError:
            print('Illegal name: {}, skipping'.format(f));
            continue;

        name = info['name'];        
        season_str = 'Season ' + str(int(info['season']));

        if(tvshows.is_extracted(extract_folder, info)):
            # print(info['name'], 'Season', info['season'], 'Episode', info['episode'], 'already exists, skipping');
            continue;

        dest_filename = None;
        try:
            episode_name = tvshows.get_episode_name(info);

            # Format filename properly, like: "Foobar - 603 - Foo Bar Baz Foo"
            dest_filename = '{} - {}{:02d} - {}'.format(name, info['season'], info['episode'], episode_name);
        except Exception as e:
            print('Error getting name for: {}, reason: {}'.format(info, e));

        src = os.path.join(download_folder, f);
        dest = os.path.join(extract_folder, name, season_str);

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
                matched_files = (f for f in local_files if re.match(extensions, f));

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


# source:               Full path to file
# dest:                 Path to destination directory
# (opt) new_filename:   Optional new filename for extracted file
def copy_file(source, dest, new_filename=None):
    #TODO: display progress
    print('Copying {} to {}'.format(source, dest));

    if(not os.path.exists(dest)):
        os.makedirs(dest);

    if(new_filename):
        new_filename = '{}.{}'.format(new_filename, re.search('.*\.(.*)$', source).groups()[0]);
        dest = os.path.join(dest, new_filename);

    shutil.copy(source, dest);

# source:               Path to directory containing archives
# dest:                 Path to destination directory
# (opt) new_filename:   Optional new filename for extracted file
def extract_file(source, dest, new_filename=None):
    files = os.listdir(source);

    rarfiles = (f for f in files if re.match('.*\.rar', f));
    filepath = os.path.join(source, next(rarfiles));

    rf = rarfile.RarFile(filepath);

    the_file = filename = rf.namelist().pop();

    if(new_filename):
        (ext, ) = re.search('.*\.(.*)$', the_file).groups();
        the_file = '{}.{}'.format(new_filename, ext);
    else:
        the_file = filename;

    print('Extracting', filename, 'to', os.path.join(dest, the_file))
    rf.extract(filename, dest);

    old_path = os.path.join(dest, filename);
    new_path = os.path.join(dest, the_file);
    os.rename(old_path, new_path);

# filepath: Full path to file w/o extension
#
# Throws: FileNotFoundError if filepath does not yield
#         a file during a scan for extensions
def get_subtitles(filepath):
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
        dl_link = tvshows.get_subtitle_link(filepath);
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


def filter_data(entries, filters):
    result = [];

    if(entries is not None and filters is not None):
        for entry in entries:
            for filt in filters:
                if(re.search(filt, entry['title'], re.IGNORECASE) is not None):
                    try:
                        info = tvshows.get_info(entry['title']);
                        if(not tvshows.is_contained(result, info)):
                            info['link'] = entry['link'];
                            result.append(info);
                    except Exception as e:
                        print('Error:', e);

    return result;

def loop_forever():
    last_rss_update = 0;
    last_scrape = 0;
    last_batch_extract = 0;
    
    while(True):
        print("looping");
        now = time.time();

        if(now - last_rss_update > RSS_INTERVAL):
            print('Updating...');
            data = feedparser.parse(feed_url);
            last_rss_update = time.time();

        if(now - last_scrape > SCRAPE_INTERVAL):
            print('Scraping...');
            scraped_torrents = scrape_torrents(max_pages=10);
            print('Found {} torrents since last scrape'.format(len(scraped_torrents)));
            data.entries.extend(scraped_torrents);
            last_scrape = time.time();

        matches = filter_data(data.entries, filters);
        batch_download(matches);

        if(now - last_batch_extract):
            print('Performing batch extract...');
            batch_extract();
            last_batch_extract = time.time();

        sleep_interval = min(RSS_INTERVAL, SCRAPE_INTERVAL, EXTRACT_INTERVAL);
        print('Sleeping for', sleep_interval, 'seconds');
        time.sleep(sleep_interval); 

if __name__ == '__main__':
    init();

    if(len(sys.argv) == 1):
        loop_forever();
    elif(sys.argv[1] == '--download-sub'):
        get_subtitles(sys.argv[2]);
    