import codecs, configparser json, math, os, struct

from xmlrpc.client import ServerProxy

API_URL = 'http://api.opensubtitles.org/xml-rpc';

config = configparser.ConfigParser();
config.read_file(codecs.open('config.ini', 'r', 'utf8'));
username = config['OS_Credentials'].get('username');
password = config['OS_Credentials'].get('password');
useragent = config['OS_Credentials'].get('useragent');

def compute_hash(filepath):
    SEEK_SET = 0;
    SEEK_CUR = 1;
    SEEK_END = 2;

    fh = open(filepath, 'rb');
    fsize = os.path.getsize(filepath);

    fhash = fsize;

    bytesize = struct.calcsize('<q');
    bytemax = int(65536 / bytesize);

    for i in range(bytemax):
        tmp = fh.read(bytesize);
        (val,) = struct.unpack('<q', tmp);
        fhash += val;
        fhash &= 0xffffffffffffffff

    fh.seek(max(0, fsize - 65536), SEEK_SET);

    for i in range(bytemax):
        tmp = fh.read(bytesize);
        (val,) = struct.unpack('<q', tmp);
        fhash += val;
        fhash &= 0xffffffffffffffff

    fh.close();

def get_subtitle_link(filepath):
    fsize = os.path.getsize(filepath);
    fhash = compute_hash(filepath);

    proxy = ServerProxy(API_URL, allow_none=True);
    res = proxy.LogIn(username, password, useragent);
    assert res.get('status') == '200 OK';
    api_token = res.get('token');

    res = proxy.SearchSubtitles(api_token, [
            {
                'sublanguageid': 'en',
                'moviehash': fhash,
                'moviebytesize': fsize
            }
        ]);

    # Make sure only english subtitles show up
    # It's strange, but specifying language in the query sometimes
    # yields non-english results
    data = res.get('data');
    data = list(filter(lambda x: x.get('ISO639') == 'en', data));

    # Sort the list in descending order by number of downloads
    data = sorted(filtered_data, key=lambda k: int(k.get('SubDownloadsCnt', 0)), reverse=True);

    download_link = data.pop().get('ZipDownloadLink');

    return download_link;
