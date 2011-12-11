# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import get_renderer
import json


@view_config(context='velruse.api.AuthenticationComplete', renderer='json')
def auth_complete_view(context, request):
    return {
        'profile': context.profile,
        'credentials': context.credentials,
    }


@view_config(context='velruse.exceptions.AuthenticationDenied',
             renderer='json')
def auth_denied_view(context, request):
    return context.args


def add_base_template(event):
    base = get_renderer('templates/base.pt').implementation()
    return event.update({'base': base})


@view_config(route_name='list', renderer='templates/list.pt')
def list_tweets(context, request):
    misc = request.registry.con['misc']
    return dict(tweets=misc.lrange('list', -10, -1),
                tweet_len=misc.llen('list'))


@view_config(route_name='random')
def random(context, request):
    key = request.registry.con['tweets'].randomkey()
    if key:
        raise HTTPFound(request.route_url('get', key=key))
    else:
        raise HTTPFound(request.route_url('about'))


@view_config(route_name='get', renderer='templates/tweet.pt')
def get(context, request):
    key = request.matchdict['key']

    tweets = request.registry.con['tweets']
    data = tweets.get(key)
    if isinstance(data, basestring):
        data = json.loads(data)

    response = {'data': data}
    if ('geo' in data and data['geo'] is not None
        and 'coordinates' in data['geo']):
        response['location'] = data['geo']['coordinates']
    else:
        response['location'] = False

    return response


@view_config(route_name='tag', renderer='templates/tag.pt')
def tag(context, request):
    tag = request.matchdict['tag']
    con = request.registry.con

    ids = con['misc'].lrange('tag:%s' % tag, 0, -1)
    if not ids:
        raise HTTPNotFound()

    # get the tweets for this tag
    tweets = []
    for idx in ids:
        tweets.append(con['tweets'].get(idx))

    return {'tweets': tweets}


@view_config(route_name='user', renderer='templates/user.pt')
def user(context, request):
    user = request.matchdict['user']
    misc = request.registry.con['misc']
    return {'tweet_ids': misc.lrange("user:%s" % user, 0, -1),
            'username': user, 'tweet_len': misc.llen('usr:%s' % user)}
