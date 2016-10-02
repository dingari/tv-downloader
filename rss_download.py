import sys

from torrent_downloader import TorrentDownloader

if __name__ == '__main__':
    downloader = TorrentDownloader('config.ini', 'filters.ini');

    if(len(sys.argv) == 1):
        downloader.loop_forever();
    elif(sys.argv[1] == '--download-sub'):
        get_subtitles(sys.argv[2]);
    