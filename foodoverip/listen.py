import os
import sys
from urlparse import urlparse

import tweepy
from ConfigObject import ConfigObject
from restkit import request
from pyquery import PyQuery
import urllib2

from foodoverip.util import JSONEncoder, get_connections

IMAGE_SERVICES = {'yfrog': '#main_image',
                  'twitpic.com': '#photo-display',
                  'lockerz.com': '#photo',
}


def get_auth(config):
    section = config['app:pyramid']
    consumer_key = section['velruse.twitter.consumer_key']
    consumer_secret = section['velruse.twitter.consumer_secret']
    access_token = section['velruse.twitter.access_token']
    token_secret = os.environ['TOKEN_SECRET']

    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, token_secret)
    return auth


def save_picture(url, destination):

    r = request(url)

    with r.body_stream() as body:
        with open(destination, 'wb') as f:
            for block in body:
                f.write(block)


def get_picture(tweet):
    print "found a picture for %s" % tweet.id

    # get the images if any and store them
    for media in tweet.entities.get('media', []):
        if media['type'] == "photo" and media['media_url']:
            return media['media_url']

    for url_ in tweet.entities['urls']:
        url = url_['expanded_url']
        try:
            d = PyQuery(url)
        except urllib2.HTTPError:
            continue
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

            # get the picture
            url = get_picture(tweet)
            if url:
                img_path = os.path.join(os.path.dirname(__file__), 'static',
                                        'images', str(tweet.id))
                save_picture(url, img_path)
                con['tweets'].set(tweet.id, encoder.encode(tweet.__dict__))
            else:
                continue

            # get tags
            tags = [h['text'] for h in tweet.entities['hashtags']
                    if h['text'] != config['app:pyramid'].hashtag]

            for tag in tags:
                con['tags'].rpush(tag, tweet.id)

            # save the user
            con['users'].rpush(tweet.from_user, tweet.id)

            # .. and his avatar if needed
            avatars_path = os.path.join(os.path.dirname(__file__),
                    'static', 'avatars')

            avatar_path = os.path.join(avatars_path, tweet.from_user)
            if not os.path.isfile(avatar_path):  # XXX the avatar can't change
                save_picture(tweet.profile_image_url, avatar_path)


def run_cli():
    config = ConfigObject(filename=sys.argv[1])

    auth = get_auth(config)
    client = tweepy.API(auth)
    parse_results(client.search(config['app:pyramid'].hashtag,
        include_entities=True), config)


if __name__ == "__main__":
    run_cli()
