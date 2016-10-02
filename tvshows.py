import math
import os
import re

from tvdb_api import refresh_api_token, get_episode_name
from opensubtitles_api import get_subtitle_link


def make_filter(name, season=None, episode=None, quality=None):
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

        result.append('((s{}e{})|{})'.format(season_str, episode_str, numeric_str));
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
def get_info(input_str):
    # Extract season and episode number
    # Currently searches for S01E01 format or 101 format
    reg_se1 = re.compile('s(\d\d)e(\d\d)', re.IGNORECASE);
    reg_se2 = re.compile('[\.\s](\d{3,4})[\.\s]');
    res_se1 = reg_se1.search(input_str);
    res_se2 = reg_se2.search(input_str);

    if(res_se1 is None and res_se2 is None):
        raise ValueError('No season/episode info found for \'{}\''.format(input_str));
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
    first_part = reg_split.split(input_str)[0];
    if(first_part is ''):
        raise ValueError('No title found');
    words = re.findall('[\.\s]*(\w+)[\.\s]*', first_part);
    name = ' '.join(words).title();

    return {'name': name, 'season': season, 'episode': episode}

def is_extracted(extract_path, info):
    name = info['name'];
    season = info['season'];
    episode = info['episode'];
    
    path = os.path.join(extract_path, name, 'Season ' + str(info['season']));

    return search(path, name=name, season=season, episode=episode);

def is_downloaded(download_path, info):
    name = info['name'];
    season = info['season'];
    episode = info['episode'];
    
    path = download_path;

    return search(path, name=name, season=season, episode=episode);

def search(path, name=None, season=None, episode=None, quality=None):
    filt = make_filter(name, season=season, episode=episode);

    try:
        for filename in os.listdir(path):
            if(re.search(filt, filename, re.IGNORECASE) is not None):
                return True;
    except Exception as e:
        return False;

    return False;

# Throws:
#   TypeError
#   KeyError
def is_contained(matched_list, info):
    new_subdict = {k: info[k] for k in ('name', 'episode', 'season')};
    new_subdict['name'] = new_subdict['name'].title();
    for entry in matched_list:
        current_subdict = {k: entry[k] for k in ('name', 'episode', 'season')};
        if(new_subdict == current_subdict):
            return True;

    return False;
