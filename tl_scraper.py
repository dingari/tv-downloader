import json, os, re, requests

import urllib.parse as urlparse

from bs4 import BeautifulSoup

# Maximum pages to scrape if last_seen_id is not hit during scrape
MAX_PAGES = 50;

class TlClient:

	host = 'https://torrentleech.org';
	login_url = host + '/user/account/login';
	browse_url = host + '/torrents/browse/index/facets/category%253ATV';

	last_seen_id = None;

	def __init__(self, username=None, password=None):
		self.username = username;
		self.password = password;

		if(self.username != None and self.password != None):
			self.login(self.username, self.password);

	def login(self, username=None, password=None):
		
		self.username = username;
		self.password = password;

		if(self.username == None or self.password == None):
			raise Exception('Must provide username and password');

		data = {
			'username': self.username,
			'password': self.password
		}

		session = requests.session();
		session.get(self.host);
		session.post(self.login_url, data = data);

		self.session = session;

	# TODO: add optional destination path parameter
	def get_torrent(self, url):
		(torrent_name, ) = re.search('.*/(.*).torrent$', url).groups();
		tmp_path = os.path.join(os.environ['TMP'], '{}.torrent'.format(torrent_name));

		if(self.session is None):
			self.login();

		res = self.session.get(url);

		with open(tmp_path, 'wb') as torrentfile:
			torrentfile.write(res.content);

		return tmp_path;

	def scrape_torrents(self, max_pages=MAX_PAGES):
		if(self.session is None):
			self.login();

		page = 1;
		results = [];
		current_id = 0;
		first_id = None;

		# global last_seen_id;

		while(page <= max_pages and current_id != self.last_seen_id):
			res = self.session.get(self.browse_url + '/page/{}'.format(page));
			soup = BeautifulSoup(res.text, 'html.parser');

			table = soup.find('table', {'id': 'torrenttable'});
			rows = table.find_all('tr');
			
			for row in rows:
				td = row.find('td', {'class': 'quickdownload'});
				
				if(td is not None):
					download_url = td.a.attrs['href'];
					(id_str, title, ) = re.match('/download/(.*)/(.*).torrent', download_url).groups();
					current_id = int(id_str);

					# Take note of the first id encountered
					first_id = current_id if first_id is None else first_id;

					if(current_id == self.last_seen_id):
						break;

					results.append({
						'link': self.host + download_url,
						'title': title
					});

			page += 1;

		self.last_seen_id = first_id;

		return results;