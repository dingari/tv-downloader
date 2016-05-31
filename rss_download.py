import codecs
import configparser
import feedparser
import math
import os
import re

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
    dest_path = config['Download'].get('destination');

    # Read filter config file
    config = configparser.ConfigParser();
    config.read_file(codecs.open('filters.ini', 'r', 'utf8'));

    # Build filter list
    for section in config.sections():
        filt = [];
        name = config[section].get('name');
        quality = config[section].get('quality');
        filters.append(rss_filter(name, quality=quality));

def rss_filter(name, **kwargs):
    season = episode = quality = None;
    if('season' in kwargs):
        season = kwargs['season'];
    if('episode' in kwargs):
        episode = kwargs['episode'];
    if('quality' in kwargs):
        quality = kwargs['quality'];

    if(name is None):
        raise ValueError('Must provide name');

    words = re.findall('\w+', name.lower());
    result = [];
    result.append(words.pop(0));

    # Build title part of regex
    while(len(words) > 0):
        result.append('[\s_\.]?');
        result.append(words.pop(0));
    result.append('.*');

    # Build season/episode part of regex
    if(season is not None):
        season_str = str(season).zfill(2);
        if(episode is not None):
            episode_str = str(episode).zfill(2);
            numeric_str = str(season*100 + episode);
        else:
            episode_str = '\d\d';
            numeric_str = str(season) + '\d\d';

        result.append('((s{}e{})|{}'.format(season_str, episode_str, numeric_str));
        result.append('.*');

    # Build quality part of regex,
    if(quality is not None):
        if(isinstance(quality, list)):
            result.append(quality.pop(0));
            while(len(quality) > 0):
                result.append('|');
                result.append(quality.pop(0).lower());
        elif isinstance(quality, str):
            result.append(quality.lower());
        result.append('.*');

    # Join all list elements and return the string
    return ''.join(result);

# Try to extract info about tv show name, season and episode
# from a given string, will raise exception if string
# can't be decoded properly
def show_info(input_str):
    # Extract season and episode number
    # Currently searches for S01E01 format or 0101 format
    reg_se1 = re.compile('s(\d\d)e(\d\d)', re.IGNORECASE);
    reg_se2 = re.compile('[\.\s](\d{3,4})[\.\s]');
    res_se1 = reg_se1.search(input_str);
    res_se2 = reg_se2.search(input_str);

    if(res_se1 is None and res_se2 is None):
        raise ValueError('No season/episode info found');
    elif(res_se2 is None):
        season = int(res_se1.group(1));
        episode = int(res_se1.group(2));
        reg_split = reg_se1;
    elif(res_se1 is None):
        se = res_se2.group(1);
        season = math.floor(int(se)/100);
        episode = int(se) % 100;
        reg_split = reg_se2;

    # Extract show name
    # TODO: try to do it more generally with regex
    #first_part = re.split('S\d\dE\d\d|\d{3,4}', input_str, re.IGNORECASE);
    first_part = reg_split.split(input_str)[0];
    if(first_part is ''):
        raise ValueError('No title found');
    words = re.findall('[\.\s]*(\w+)[\.\s]*', first_part);
    name = ' '.join(words).title();

    return {'name': name, 'season': season, 'episode': episode}

def batch_download(matched_list):
    for entry in matched_list:
        if(not tvshow_exists(entry)):
            init_download(url);

def init_download(url):
    print('Downloading from:', url);
    #Popen([client_path, '/DIRECTORY', dest_path, url]);

def tvshow_exists(root_dir, info):
    # TODO: Not fully implemented
    filt = rss_filter(info['name'], None);

    name = info['name']
    season = 'Season ' + str(info['season'])
    path = os.path.join(root_dir, name, season);

    for filename in os.listdir(path):
        if(re.search(filt, filename, re.IGNORECASE) is not None):
            return True;

    print(files);

# Throws:
#   TypeError
#   KeyError
def contains_episode(matched_list, info):
    new_subdict = {k: info[k] for k in ('name', 'episode', 'season')};
    new_subdict['name'] = new_subdict['name'].title();
    for entry in matched_list:
        current_subdict = {k: entry[k] for k in ('name', 'episode', 'season')};
        if(new_subdict == current_subdict):
            return True;

    return False;

def filter_data(entries, filters):
    result = [];

    if(entries is not None and filters is not None):
        for entry in entries:
            #print(entry['title']);
            for filt in filters:
                if(re.search(filt, entry['title'], re.IGNORECASE) is not None):
                    try:
                        info = show_info(entry['title']);
                        if(not contains_episode(result, info)):
                            info['link'] = entry['link'];
                            result.append(info);
                    except Error as e:
                        print('Error:', e.strerror);

    return result;

# Read and filter feed
def update():
    print('Updating...');
    data = feedparser.parse(feed_url);
    matches = filter_data(data.entries, filters);

    #print('Result:', matches);
    for match in matches:
        print(match['name'], 's' + str(match['season']), 'e' + str(match['episode']))

if __name__ == '__main__':
    init();
    update();
