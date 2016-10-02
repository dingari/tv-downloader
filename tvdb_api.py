import codecs, configparser, json, requests

import urllib.parse as urlparse

from http.client import HTTPException

config = configparser.ConfigParser();
config.read_file(codecs.open('config.ini', 'r', 'utf8'));

class TvdbClient:

    base_url = 'https://api.thetvdb.com';

    api_token = None;
    api_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };

    def __init__(self, username=None, userkey=None, apikey=None):
        self.username = username;
        self.userkey = userkey;
        self.apikey = apikey;

        if(self.username != None and
            self.userkey != None and
            self.apikey != None):
            self.login(self.username, self.userkey, self.apikey);

    def login(self, username=None, userkey=None, apikey=None):
        payload = {
            'apikey': apikey,
            'username': username,
            'userkey': userkey
            };

        res = requests.post(
            self.base_url + '/login', 
            json=payload, 
            headers=self.api_headers);
        self.api_token = json.loads(res.text).get('token');

        if(res.status_code == 200):
            self.api_headers['Authorization'] = 'Bearer ' + self.api_token;
        else:
            raise HTTPException('TVDB API login failed: {}'.format(res.text));

    def refresh_api_token(self):
        res = requests.get(self.base_url + '/refresh_token', headers=self.api_headers);
        api_token = json.loads(res.text).get('token');

        if(res.status_code == 200):
            self.api_headers['Authorization'] = 'Bearer ' + api_token;
        else:
            raise HTTPException('Can\' refresh TVDB API token: {}'.format(res.text));

    # TODO: handle error instances (no results, multiple results)
    def get_episode_name(self, infostruct):
        try:
            self.refresh_api_token();
        except HTTPException:
            self.login();

        # Get series id
        query_string = urlparse.urlencode({'name': infostruct.get('name')});
        req_url = self.base_url + '/search/series?' + query_string;
        res = requests.get(req_url, headers=self.api_headers);

        json_data = json.loads(res.text).get('data');

        # This is ridiculous, make a loop instead?
        index_matches = (i for i, data in enumerate(json_data) if data.get('seriesName').lower() == infostruct['name'].lower() or next(alias for j, alias in enumerate(data.get('aliases')) if alias.lower() == infostruct['name'].lower()));

        series_id = json_data[next(index_matches)].get('id');

        # Use series id to get the episode name
        query_string = urlparse.urlencode({
            'airedSeason': infostruct.get('season'),
            'airedEpisode': infostruct.get('episode')
            });

        req_url = self.base_url + '/series/' + str(series_id) + '/episodes/query?' + query_string;
        res = requests.get(req_url, headers=self.api_headers);

        json_error = json.loads(res.text).get('error');
        json_data = json.loads(res.text).get('data');

        if(json_error):
            raise Exception(json_error);
            
        episode_name = json_data[0].get('episodeName');

        return episode_name;