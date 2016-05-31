import codecs
import configparser
import feedparser
import os
import re
import tvshows

from subprocess import Popen
from tl_scraper import scrape_torrents

# Globals
feed_url = '';
client_path = '';
dest_path = '';
matches = [];
filters = [];

def init():
    print('init')
    
    # Read general config file
    global feed_url;
    global client_path;
    global dest_path;
    
    config = configparser.ConfigParser();
    config.read_file(codecs.open('config.ini', 'r', 'utf8'));
    feed_url = config['RSS'].get('rss_feed');
    client_path = config['Download'].get('client_path');
    download_path = config['Download'].get('download_path');
    extract_path = config['Download'].get('extract_path');

    # Read filter config file
    config = configparser.ConfigParser();
    config.read_file(codecs.open('filters.ini', 'r', 'utf8'));

    # Build filter list
    for section in config.sections():
        filt = [];
        name = config[section].get('name');
        quality = config[section].get('quality');
        filters.append(tvshows.make_filter(name, quality=quality));

def batch_download(matched_list):
    for entry in matched_list:
        if(not is_tvshow_downloaded(entry)):
            init_download(url);

def batch_extract():
    return;

def init_download(url):
    print('Downloading from:', url);
    #Popen([client_path, '/DIRECTORY', dest_path, url]);

def filter_data(entries, filters):
    result = [];

    if(entries is not None and filters is not None):
        for entry in entries:
            #print(entry['title']);
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

# Read and filter feed
def update():
    print('Updating...');
    data = feedparser.parse(feed_url);
    matches = filter_data(data.entries, filters);

    #scrape_matches = filter_data(scrape_torrents(), filters);

    #print('Result:', matches);
    for match in matches:
        print(match['name'], 's' + str(match['season']), 'e' + str(match['episode']))

if __name__ == '__main__':
    init();
    update();