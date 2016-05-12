import codecs
import configparser
import feedparser
import math
import re

from subprocess import Popen

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
    dest_path = config['Download'].get('destination');

    # Read filter config file
    config = configparser.ConfigParser();
    config.read_file(codecs.open('filters.ini', 'r', 'utf8'));

    # Build filter list
    for section in config.sections():
        filt = [];
        name = config[section].get('name');
        quality = config[section].get('quality');
        filters.append(rss_filter(name, quality));

def rss_filter(name, quality):
    words = re.findall('\w+', name)
    result = []
    result.append(words.pop(0));

    # Build title part of regex
    while(len(words) > 0):
        result.append('[\s_\.]?');
        result.append(words.pop(0));
    result.append('.*');

    # Build quality part of regex,
    if(quality is not None):
        if(isinstance(quality, list)):
            result.append(quality.pop(0));
            while(len(quality) > 0):
                result.append('|');
                result.append(quality.pop(0));
        elif isinstance(quality, str):
            result.append(quality);
        result.append('.*');

    # Join all list elements and return the string
    return ''.join(result);

# Try to extract info about tv show name, season and episode
# from a given string, will raise exception if string
# can't be decoded properly
def show_info(input_str):
    # Extract show name
    # TODO: try to do it more generally with regex
    showName = re.split('S\d+E\d+|\d{3,4}', input_str, re.IGNORECASE)[0];
    showName = showName.replace('.', ' ').strip();

    # Extract season and episode number
    # Currently searches for S01E01 format or 0101 format
    reg_se1 = re.compile('s(\d\d)e(\d\d)', re.IGNORECASE);
    reg_se2 = re.compile('[\.\s](\d{3,4})[\.\s]');
    res_se1 = reg_se1.search(input_str);
    res_se2 = reg_se2.search(input_str);

    if(res_se1 is None and res_se2 is None):
        raise Exception('Input format invalid');
    elif(res_se2 is None):
        season = int(res_se1.group(1));
        episode = int(res_se1.group(2));
    elif(res_se1 is None):
        se = res2.group(1);
        season = math.floor(int(se)/100);
        episode = int(se) % 100;

    return {'name': showName, 'season': season, 'episode': episode}

def init_download(info, url):
    print('Downloading', info);

    check_if_exists(info);

    #Popen([client_path, '/DIRECTORY', dest_path, url]);

def check_if_exists(info):
    # TODO: implement, search destination folder for given info
    return;

def contains_episode(matched_list, info):
    new_subdict = {k: info[k] for k in ('name', 'episode', 'season')};
    for entry in matched_list:
        current_subdict = {k: entry[k] for k in ('name', 'episode', 'season')};
        if(new_subdict == current_subdict):
            return True;

    return False;

# Read and filter feed
def update():
    print('Updating...');
    data = feedparser.parse(feed_url);

    for entry in data.entries:
        #print(entry.title);
        for filt in filters:
            if(re.search(filt, entry.title, re.IGNORECASE) is not None):
                try:
                    info = show_info(entry.title);
                    if(not contains_episode(matches, info)):
                        info['link'] = entry.link;
                        matches.append(info);
                except:
                    print('Invalid shit')

    print('Result:', matches);

if __name__ == '__main__':
    init();
    update();
