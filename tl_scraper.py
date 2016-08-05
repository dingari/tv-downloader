import codecs
import configparser
import requests

from bs4 import BeautifulSoup

config = configparser.ConfigParser();
config.read_file(codecs.open('config.ini', 'r', 'utf8'));
username = config['Credentials'].get('username');
password = config['Credentials'].get('password');

host = 'https://torrentleech.org';
login_url = host + '/user/account/login';
browse_url = host + '/torrents/browse/index/facets/category%253ATV';

def login(username=username, password=password, login_url=login_url):
	data = {
		'username': username,
		'password': password
	}

	session = requests.session();
	session.get(host);
	session.post(login_url, data = data);
	return session;

def scrape_torrents(session=login()):
	res = session.get(browse_url);
	soup = BeautifulSoup(res.text, 'html.parser');

	table = soup.find('table', {'id': 'torrenttable'});
	rows = table.find_all('tr');

	results = [];
	for row in rows:
		span = row.find('span', {'class': 'title'});

		if(span is not None):
			download_url = span.a.attrs['href'];
			title = span.a.text;

			results.append({
				'link': host + download_url,
				'title': title
			});

	return results;


if __name__ == '__main__':
	session = login(username, password, login_url);
	torrents = scrape_torrents(session);
	
	print(torrents);

