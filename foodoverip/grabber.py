# -*- coding: utf-8 -

import argparse
import ConfigParser
from io import BytesIO
import imghdr
import json
import os
import urllib
import urlparse

import couchdbkit
from gevent import monkey
monkey.noisy = False
monkey.patch_all()
import gevent
from gevent.queue import JoinableQueue
import Image
from pyquery import PyQuery
import restkit
from restkit.globals import set_manager
from restkit.manager.mgevent import GeventManager

set_manager(GeventManager(timeout=300))

ctypes = {'gif': 'image/gif',
          'png': 'image/png',
          'jpeg': 'image/jpeg'}


def get_db(server_uri, db_name):
    s = couchdbkit.Server(server_uri)
    return s.get_or_create_db(db_name)


def send_attachment(db, tweet, url, attname):
    res = restkit.request(url)

    if res.status_int == 200:
        img = Image.open(BytesIO(res.body_string()))

        out = BytesIO()
        img.save(out, 'png')
        print "save %s in %s as %s" % (url, tweet['_id'],"%s.png" % attname)
        db.put_attachment(tweet, out, "%s.png" % attname,
                headers={'Transfer-Encoding': 'chunked'})


class ImageFetcher(object):
    HANDLERS = {'twitpic.com': 'twitpic',
                'yfrog.com': 'yfrog',
                'flickr.com': 'flickr',
                'flic.kr': 'flickr',
                'lockerz.com': 'lockerz',
                'twitgoo.com': 'twitgoo',
                'img.ly': 'imgly',
                'plixi.com': 'lockerz',
                'twitrpix.com': 'twitrpix',
                'shozu.com': 'shozu',
                'moby.to': 'moby',
                'mobypicture.com': 'moby',
                'twitsnaps.com': 'twitsnaps',
                'instagr.am': 'instagram'}


    def __init__(self, db, tweet):
        self.db = db
        self.tweet = tweet

    def process(self):
        entities = self.tweet.get('entities', {})

        # if we are lucky, twitter already did the jo for us by getting
        # the media url
        # See: https://dev.twitter.com/docs/tco-url-wrapper/tco-redirection-behavior
        for media in entities.get('media', []):
            if media.get('type') == 'photo' and \
                    media.get('media_url') is not None:
                return send_attachment(self.db, self.tweet, media.get('media_url'), 'photo')

        # do the painful job to parse the url
        for url in entities.get('urls', []):
            if url.get('expanded_url') is not None:
                purl = urlparse.urlparse(url['expanded_url'])
                if purl.netloc in self.HANDLERS:
                    handler = self.HANDLERS[purl.netloc]
                    try:
                        return getattr(self, 'handle_%s' % handler)(purl)
                    except:
                        pass

    def scrap_url(self, url, selector, attr='src'):
        d = PyQuery(url)
        img = d(selector)
        imgurl = img[0].attrib(attr)
        send_attachment(self.db, self.tweet, imgurl, 'photo')


    def handle_twitpic(self, purl):
        self.scrap_url(purl.get_url(), 'img#photo-display')

    def handle_yfrog(self, purl):
        self.scrap_url(purl.get_url(), 'img#main_image')

    def handle_lockerz(self, purl):
        self.scrap_url(purl.get_url(), 'img#photo')

    def handle_flickr(self, purl):
        self.scrap_url(purl.get_url(), '.photo-div img')

    def handle_twitgoo(self, purl):
        self.scrap_url(purl.get_url(), 'img#fullsize')

    def handle_imgly(self, purl):
        self.scrap_url(purl.get_url(), 'img#the-image')

    def handle_twitrpix(self, purl):
        self.scrap_url(purl.get_url(), 'img#tp_image')

    def handle_shozu(self, purl):
        r = restkit.request(purl.get_url())
        self.scrap_url(r.location, 'div.clr div a', attr='href')

    def handle_mobi(self, purl):
        self.scrap_url(purl.get_url(), 'img#main_picture')

    def handle_twitsnaps(self, purl):
        self.scrap_url(purl.get_url(), 'div#main_image img')

    def handle_instagram(self, purl):
        self.scrap_url(purl.get_url(), 'img.photo')


def attach_food_img(db, tweet):
    fetcher = ImageFetcher(db, tweet)
    fetcher.process()


def tweet_worker(db, q):
    while True:
        tweet = q.get()
        try:
            txt = tweet['text'].strip()
            if txt.startswith('RT'):
                tweet['_id'] = "rt/" + tweet['id_str']
                rt = True
            else:
                tweet['_id'] = "t/" + tweet['id_str']
                rt = False

            if not db.doc_exist(tweet['_id']):
                db.save_doc(tweet)

            print tweet
            # attach profil image to the tweet
            if 'profile_image_url' in tweet:
                send_attachment(db, tweet, tweet['profile_image_url'],
                    'profile')

            # if this isn't an rt get food image, and attach it to the
            # tweet
            if not rt:
                attach_food_img(db, tweet)
        finally:
            q.task_done()

def search_twitter(db, q, since="", concurrency=10):
    base_url = "http://search.twitter.com/search.json"
    params = {"q": q, "include_entities": "true"}
    if since:
        params.update({"since": since})

    path = "?" + urllib.urlencode(params)

    found = 0
    queue = JoinableQueue()
    for i in range(concurrency):
        gevent.spawn(tweet_worker, db, queue)

    while True:
        print base_url + path
        resp = restkit.request(base_url + path)
        with resp.body_stream() as stream:
            res = json.load(stream)
            results = res.get('results')
            found += len(results)
            for result in results:
                queue.put(result)

            if "next_page" in res:
                path = res["next_page"]
            else:
                break

            if since != res['max_id']:
                since = str(res['max_id'])

    # block until all tweets has been saved
    queue.join()

    db.save_doc({"_id": "status", "since": since},
            force_update=True)
    return (since, found)



def run():
    parser = argparse.ArgumentParser(
            description='grab foodoverip images from twiiter')

    parser.add_argument(
        '-c',
        type=str,
        default="",
        help="""\
            Path to the config file.
            """)

    args = parser.parse_args()

    db_name = 'foodoverip'
    server_uri = 'http://127.0.0.1:5984'
    concurrency = 10
    q = '#foodoverip'
    refresh_time = 10.0

    # TODO: improve this ugly part there's surely a better way to handle
    # that.
    if args.c:
        config_path = os.path.expanduser(args.c)
        if os.path.exists(config_path):
            config = ConfigParser.ConfigParser()
            config.read(args.c)
            if config.has_option('foodoverip', 'server_uri'):
                server_uri = config.get('foodoverip', 'server_uri')

            if config.has_option('foodoverip', 'db'):
                db_name = config.get('foodoverip', 'db')

            if config.has_option('foodoverip', 'concurreny'):
                concurrency = config.getint('foodoverip', 'concurrency')

            if config.has_option('foodoverip', 'q'):
                q = config.get('foodoverip', 'q')

            if config.has_option('foodoverip', 'refresh_time'):
                refresh_time = config.getfloat('foodoverip', 'refresh_time')
    db = get_db(server_uri, db_name)

    since = 0
    while True:
        since, found = search_twitter(db, q, since=since,
                concurrency=concurrency)

        print "Last id: %s - Found: %s " % (since, found)
        gevent.sleep(refresh_time)




if __name__ == "__main__":
    """db = get_db()

    while True:
        since, found = search_twitter(db, "#foodoverip")
        time.sleep(5.0)
        print "Last id: %s - Found: %s " % (since, found)"""

    run()
