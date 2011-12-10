import tweepy
from ConfigObject import ConfigObject
import os
import sys
import redis
import json


def get_auth(filename):
    config = ConfigObject(filename=filename)

    section = config['app:main']
    consumer_key = section['velruse.twitter.consumer_key']
    consumer_secret = section['velruse.twitter.consumer_secret']
    access_token = section['velruse.twitter.access_token']
    token_secret = os.environ['TOKEN_SECRET']

    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, token_secret)
    return auth


def parse_results(results):
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    cli = redis.Redis(connection_pool=pool)

    for result in results:
        if not cli.get(result.id) and not result.text.startswith("RT"):
            cli.set(result.id, json.dumps(result.__dict__))


def run_cli():
    auth = get_auth(sys.argv[1])
    client = tweepy.API(auth)
    parse_results(client.search("#foodoverip", include_entities=True))
