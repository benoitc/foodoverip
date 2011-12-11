import os
import sys
from urlparse import urlparse

import tweepy
from ConfigObject import ConfigObject
from restkit import request
from pyquery import PyQuery

from foodoverip.util import JSONEncoder, get_connections

IMAGE_SERVICES = {'yfrog': '#main_image',
                  'twitpic.com': '#photo-display',
                  'lockerz.com': '#photo',
}


def get_auth(config):
    section = config['app:main']
    consumer_key = section['velruse.twitter.consumer_key']
    consumer_secret = section['velruse.twitter.consumer_secret']
    access_token = section['velruse.twitter.access_token']
    token_secret = os.environ['TOKEN_SECRET']

    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, token_secret)
    return auth


def save_picture(id, url):

    img_path = os.path.join(os.path.dirname(__file__), 'static', 'images')

    r = request(url)

    with r.body_stream() as body:
        with open(os.path.join(img_path, str(id)), 'wb') as f:
            for block in body:
                f.write(block)


def get_picture(tweet):

    # get the images if any and store them
    for media in tweet.entities.get('media', []):
        if media['type'] == "photo" and media['media_url']:
            return media['media_url']

    for url_ in tweet.entities['urls']:
        url = url_['expanded_url']
        d = PyQuery(url)
        selector = IMAGE_SERVICES.get(urlparse(url).netloc, None)
        if selector:
            images = d("img%s" % selector)
            if images:
                return images[0].attrib['src']

    return None


def parse_results(results, config):
    con = get_connections()

    encoder = JSONEncoder()

    for tweet in results:

        if not con['tweets'].exists(tweet.id) \
           and not tweet.text.startswith("RT"):

            con['tweets'].set(tweet.id, encoder.encode(tweet.__dict__))
            url = get_picture(tweet)
            if url:
                save_picture(tweet.id, url)
            # get tags

            tags = [h['text'] for h in tweet.entities['hashtags']
                    if h['text'] != config['app:main'].hashtag]

            for tag in tags:
                con['tags'].rpush(tag, tweet.id)


def run_cli():
    config = ConfigObject(filename=sys.argv[1])

    auth = get_auth(config)
    client = tweepy.API(auth)
    parse_results(client.search(config['app:main'].hashtag,
        include_entities=True), config)
