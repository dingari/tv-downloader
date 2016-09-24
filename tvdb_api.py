import codecs, configparser, json, requests

import urllib.parse as urlparse

from http.client import HTTPException

config = configparser.ConfigParser();
config.read_file(codecs.open('config.ini', 'r', 'utf8'));
username = config['TVDB_Credentials'].get('username');
userkey = config['TVDB_Credentials'].get('userkey');
apikey = config['TVDB_Credentials'].get('apikey');

API_URL = 'https://api.thetvdb.com';

api_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE0NzQ0OTY2NDMsImlkIjoidHYtZG93bmxvYWRlciIsIm9yaWdfaWF0IjoxNDc0NDEwMjQzLCJ1c2VyaWQiOjQ2MjU5MSwidXNlcm5hbWUiOiJkaW5nYXJpIn0.1WMJeYXvqIbp4VcDAPc4ZWXHvUN8UERTEhrdjI_oi6yXNvseh3WA668XsxPODiIVFID1sk3RJOanS2_htwdyXgiD1z8p_ENIj_QIq5F3qaz5JJgPVwxahTtm3y6ohXsziF5tFZo577tQbvbsEcZgF9FrEhSjrSON3fPMhXlXC5XN6Mdq1NhdaDpfuqp8ATHvsUWDin6Err1QcQpg48MfwH4N_njWRPF34nEj8e-bkrOk6bEfREq9wZgnUcFk5Q2ryAI3-uT69qUjiwza9ufvmeuxDhfub6EEbTy4_wDFkm8F37O0d-EtKb1RAydaHdQFhgaEsG1VzEsLtPI_bgcWCw'
api_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
};

def login():
    global api_token;

    payload = {
        'apikey': apikey,
        'username': username,
        'userkey': userkey
        };

    res = requests.post(API_URL + '/login', json=payload, headers=api_headers);
    api_token = json.loads(res.text).get('token');

    if(res.status_code == 200):
        api_headers['Authorization'] = 'Bearer ' + api_token;
    else:
        raise HTTPException('TVDB API login failed: {}'.format(res.text));

def refresh_api_token():
    global api_token;

    res = requests.get(API_URL + '/refresh_token', headers=api_headers);
    api_token = json.loads(res.text).get('token');

    if(res.status_code == 200):
        api_headers['Authorization'] = 'Bearer ' + api_token;
    else:
        raise HTTPException('Can\' refresh TVDB API token: {}'.format(res.text));

# TODO: handle error instances (no results, multiple results)
def get_episode_name(info):
    try:
        refresh_api_token();
    except HTTPException:
        login();

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