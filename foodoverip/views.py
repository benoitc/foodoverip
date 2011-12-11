# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer, render_to_response
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


@view_config(route_name='random')
def random(context, request):
    key = request.registry.con['tweets'].randomkey()
    raise HTTPFound(request.route_url('get', key=key))


@view_config(route_name='get', renderer='templates/index.pt')
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
    tag = request.matchdict('tag')
    con = request.registry['con']

    ids = con.tags.lrange(tag, 0, -1)
    if not ids:
        raise HTTPNotFound()

    # get the tweets for this tag
    tweets = []
    for id in ids:
        tweets.append(con.tweets.get(id))

    return {'tweets': tweets}
