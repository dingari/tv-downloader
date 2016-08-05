import codecs
import configparser
import feedparser
import os
import rarfile
import re
import shutil
import time
import tvshows

from subprocess import Popen
from tl_scraper import scrape_torrents

# Globals
feed_url = '';
client_path = '';
download_folder = '';

extract_tool_path = '';
extract_folder = '';
extensions = '';

matches = [];
filters = [];

RSS_INTERVAL = 1 * 60 * 60;
SCRAPE_INTERVAL = 6 * 60 * 60;

last_rss_update = 0;
last_scrape = 0;

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
    # Popen([client_path, '/DIRECTORY', download_folder, url]);

def batch_download(matched_list):
    for entry in matched_list:
        if(not is_downloaded(entry)):
            init_download(url);

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
            print(info['name'], 'Season', info['season'], 'Episode', info['episode'], 'already exists, skipping');
            continue;

        src = os.path.join(download_folder, f);
        dest = os.path.join(extract_folder, name, season_str);

        # If we find a single file, copy it
        if(os.path.isfile(src)):
            copy_file(src, dest);      
            continue;
        else:
            # Look for .rar files and try to extract
            try:
                extract_file(src, dest);
            except:
                # If extraction fails, look for a single file within the directory
                # and copy it, if one is found
                local_files = os.listdir(src);
                matched_files = (f for f in local_files if re.match(extensions, f));

                try:
                    filename = next(matched_files);
                    copy_file(os.path.join(src, filename), dest);
                except:
                    print('An error occured while processing {}, skipping'.format(src));

# source: Full path to file
# dest: Path to destination directory
def copy_file(source, dest):
    #TODO: display progress
    print('Copying {} to {}'.format(source, dest));

    if(not os.path.exists(dest)):
        os.makedirs(dest);

    shutil.copy(source, dest);

# source: Path to directory containing archives
# dest: Path to destination directory
def extract_file(source, dest):
    files = os.listdir(source);

    rarfiles = (f for f in files if re.match('.*\.rar', f));
    filepath = os.path.join(source, next(rarfiles));

    rf = rarfile.RarFile(filepath);

    the_file = rf.namelist().pop();

    print('Extracting', the_file, 'to', os.path.join(dest, the_file))
    rf.extract(the_file, dest);

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

if __name__ == '__main__':
    init();

    batch_extract();

    # while(True):
    #     print("looping");

    #     now = time.time();
    #     if(now - last_rss_update > RSS_INTERVAL):
    #         print('Updating...');
    #         data = feedparser.parse(feed_url);
    #         last_rss_update = time.time();

    #         if(now - last_scrape > SCRAPE_INTERVAL):
    #             print('Scraping...');
    #             data.entries.extend(scrape_torrents());
    #             last_scrape = time.time();

    #     matches = filter_data(data.entries, filters);

    #     sleep_interval = min(RSS_INTERVAL, SCRAPE_INTERVAL);
    #     print('Sleeping for', sleep_interval, 'seconds');
    #     time.sleep(sleep_interval);

