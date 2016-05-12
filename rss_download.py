import codecs
import configparser
import feedparser
import re

from subprocess import Popen

config = configparser.ConfigParser();
config.read_file(codecs.open('config.ini', 'r', 'utf8'));
feed_url = config['RSS'].get('rss_feed');
client_path = config['Download'].get('client_path');
dest_path = config['Download'].get('destination');

matches = [];
filters = [];

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

def show_info(dirname):
    showName = re.split('S\d+E\d+|\d{3,4}', dirname, re.IGNORECASE)[0]
    showName = showName.replace('.', ' ').strip()

    res1 = re.search('S\d+E\d+', dirname, re.IGNORECASE)
    res2 = re.search('\d{3,4}', dirname)

    if(res1 is not None):
        SE = res1.group().split('S')[1].split('E')
        season = int(SE[0])
        episode = int(SE[1])
    elif(res2 is not None):
        se = res2.group()
        season = math.floor(int(se)/100)
        episode = int(se) % 100

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

def update():
    print('Updating...');
    data = feedparser.parse(feed_url);
    filters.append(rss_filter('family feud nz', None));

    for entry in data.entries:
        #print(entry.title);
        for filt in filters:
            if(re.search(filt, entry.title, re.IGNORECASE) is not None):
                info = show_info(entry.title);
                if(not contains_episode(matches, info)):
                    info['link'] = entry.link;
                    matches.append(info);

    print('Result:', matches);

if __name__ == '__main__':
    update();
