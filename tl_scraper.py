import codecs
import configparser
import json
import re
import requests

import urllib.parse as urlparse

from bs4 import BeautifulSoup

config = configparser.ConfigParser();
config.read_file(codecs.open('config.ini', 'r', 'utf8'));
username = config['TL_Credentials'].get('username');
password = config['TL_Credentials'].get('password');

host = 'https://torrentleech.org';
login_url = host + '/user/account/login';
browse_url = host + '/torrents/browse/index/facets/category%253ATV';

# Variable representing the FIRST torrent id encountered during last scrape,
last_seen_id = None;

def login(username=username, password=password, login_url=login_url):
	data = {
		'username': username,
		'password': password
	}

	session = requests.session();
	session.get(host);
	session.post(login_url, data = data);
	return session;

def scrape_torrents(session=login(), max_pages=10):
	page = 1;
	results = [];
	current_id = 0;
	first_id = None;

	global last_seen_id;

	while(page <= max_pages and current_id != last_seen_id):
		res = session.get(browse_url + '/page/{}'.format(page));
		soup = BeautifulSoup(res.text, 'html.parser');

		table = soup.find('table', {'id': 'torrenttable'});
		rows = table.find_all('tr');
		
		for row in rows:
			td = row.find('td', {'class': 'quickdownload'});
			
			if(td is not None):
				download_url = td.a.attrs['href'];
				(id_str, title, ) = re.match('/download/(.*)/(.*).torrent', download_url).groups();
				current_id = int(id_str);

				first_id = current_id if first_id is None else first_id;

				if(current_id == last_seen_id):
					break;

				results.append({
					'link': host + download_url,
					'title': title
				});

		page += 1;

	last_seen_id = first_id;

	return results;


if __name__ == '__main__':
	session = login(username, password, login_url);
	torrents = scrape_torrents(session);
	
	print(json.dumps(torrents, indent=4));

	print('Found {} torrents'.format(len(torrents)));
	print('last_seen_id = {}'.format(last_seen_id));

