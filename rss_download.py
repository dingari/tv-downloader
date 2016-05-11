import configparser
import feedparser
import re

config = configparser.ConfigParser();
config.read('config.ini');
feed_url = config['RSS'].get('rss_feed');

data = feedparser.parse(feed_url);

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
        season = SE[0]
        episode = SE[1]
    elif(res2 is not None):
        se = res2.group()
        season = math.floor(int(se)/100)
        episode = int(se) % 100

    return [showName, season, episode]

def main():
    filt = rss_filter('Chicago Fire', '720p');
    matches = {};
    for entry in data.entries:
        #print(entry.title);
        if(re.match(filt, entry.title) is not None):
           info = show_info(entry.title);
           print(info);

    print(filt);

main();
