import json, requests

import urllib.parse as urlparse

from http.client import HTTPException

API_URL = 'https://api.thetvdb.com';

api_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE0NzQ0MDk2MjcsImlkIjoidHYtZG93bmxvYWRlciIsIm9yaWdfaWF0IjoxNDc0MzIzMjI3LCJ1c2VyaWQiOjQ2MjU5MSwidXNlcm5hbWUiOiJkaW5nYXJpIn0.HAqUnnLJg4prf1v3Q0XP7JjyAeRahrcjhQJ99G1EcYJEPQQ2wLsPMV4avvAf1zJQpX5G_XPTyGtqAUf6ljnmbojnIQRL-c26Iq0b5P160kixBMnUwQoK5Py14AEKR6G4zKjdtBO37JqvcWaElsgBzjfY8zypsJXickzsLAfBLVoh3f893p2ZU7UgYFCJOPZ7km-6GKhMLIO5FLGWx2Psja54XbBowI1TZOIgNAh3yxOD561hvRno9dlIZ7VaG3DxX8OyA6LHno6eoeyQAF1H9mscbLZcLWkBOFLBzJyH_gLfhZfENaseACB5-Nld188Xq-OkCMfrXUVNHRz2jWXpxw'
api_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + api_token
};

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

    # This is ridiculous, make a loop instead?
    index_matches = (i for i, data in enumerate(json_data) if data.get('seriesName').lower() == info['name'].lower() or next(alias for j, alias in enumerate(data.get('aliases')) if alias.lower() == info['name'].lower()));

    series_id = json_data[next(index_matches)].get('id');

    # Use series id to get the episode name
    query_string = urlparse.urlencode({
        'airedSeason': info.get('season'),
        'airedEpisode': info.get('episode')
        });
    req_url = API_URL + '/series/' + str(series_id) + '/episodes/query?' + query_string;
    res = requests.get(req_url, headers=api_headers);

    json_error = json.loads(res.text).get('error');
    json_data = json.loads(res.text).get('data');

    if(json_error):
        raise Exception(json_error);
        
    episode_name = json_data[0].get('episodeName');

    return episode_name;