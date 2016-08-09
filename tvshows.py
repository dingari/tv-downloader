import json
import math
import os
import re
import requests
import urllib.parse as urlparse

from http.client import HTTPException

API_URL = 'https://api.thetvdb.com';

api_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE0NzA4MTYwMTksImlkIjoidHYtZG93bmxvYWRlciIsIm9yaWdfaWF0IjoxNDcwNzI5NjE5LCJ1c2VyaWQiOjQ2MjU5MSwidXNlcm5hbWUiOiJkaW5nYXJpIn0.3JSuzkrut8ayMj2gmgd05kf-OwJmwMi_S1ydhWEYdZ9s7yrcKon-iBvhYjCMx3EOwU5BRfQovSBLy-W5pFUmyXRh4R_y-cLcha-UwJRgg-OHYLquYaN98Em1kYiRz6Yq8__80oo-XNYhEYREcbIy2M76zIoNxmPBwionuFy5romhGVh0WNtbOwQtu-n2bcAQ2qePTYf0saI9h7cYwEN3yPVE40W-jBe1b36xPvuW0hjDU-w1dIpQtiUa4iFJ5SIY3PH3MerffcDeGJSBCKWy_4bwqUxscmAR54yt010kmOYHND9nZKPt7s39ba7oUNyBX-UX1kfQNf2fwnmcj45WnA';

api_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + api_token
};

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

def refresh_api_token():
    global api_token;

    res = requests.get(API_URL + '/refresh_token', headers=api_headers);
    api_token = json.loads(res.text).get('token');

    if(res.status_code == 200):
        api_headers['Authorization'] = 'Bearer ' + api_token;
    else:
        raise HTTPException('Error, response code: {}'.format(res.status_code));

# TODO: handle error instances (no results, multiple results)
def get_episode_name(info):
    # Get series id
    query_string = urlparse.urlencode({'name': info['name']});
    req_url = API_URL + '/search/series?' + query_string;
    res = requests.get(req_url, headers=api_headers);

    json_data = json.loads(res.text).get('data');

    index_matches = (i for i, d in enumerate(json_data) if json_data[i].get('seriesName').lower() == info['name'].lower());
    series_id = json_data[next(index_matches)].get('id');

    # Use series id to get the episode name
    query_string = urlparse.urlencode({
        'airedSeason': info.get('season'),
        'airedEpisode': info.get('episode')
        });
    req_url = API_URL + '/series/' + str(series_id) + '/episodes/query?' + query_string;
    res = requests.get(req_url, headers=api_headers);

    json_data = json.loads(res.text).get('data');
    episode_name = json_data[0].get('episodeName');

    return episode_name;