import json, math, os, struct

from xmlrpc.client import ServerProxy

class OpenSubtitlesClient:

    api_url = 'http://api.opensubtitles.org/xml-rpc';
    lang_ISO639 = 'en';

    def __init__(self, username=None, password=None, useragent=None):
        self.username = username;
        self.password = password;
        self.useragent = useragent;

    def get_subtitle_link(self, filepath):
        fsize = os.path.getsize(filepath);
        fhash = self.compute_hash(filepath);

        proxy = ServerProxy(self.api_url, allow_none=True);
        res = proxy.LogIn(
            self.username, 
            self.password, 
            self.lang_ISO639, 
            self.useragent
        );
        
        if(res.get('status') == 200):
            raise HTTPException('OS API login failed: {}'.format(res.text));

        self.api_token = res.get('token');

        res = proxy.SearchSubtitles(self.api_token, [
                {
                    'sublanguageid': self.lang_ISO639,
                    'moviehash': fhash,
                    'moviebytesize': str(fsize)
                }
            ]);

        # Make sure only english subtitles show up
        # It's strange, but specifying language in the query sometimes
        # yields non-english results
        data = res.get('data');
        data = list(filter(lambda x: x.get('ISO639') == self.lang_ISO639, data));

        # Sort the list in descending order by number of downloads
        data = sorted(data, key=lambda k: int(k.get('SubDownloadsCnt', 0)), reverse=True);

        download_link = data.pop().get('ZipDownloadLink');

        return download_link;

    def compute_hash(self, filepath):
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