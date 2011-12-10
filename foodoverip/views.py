# -*- coding: utf-8 -*-
from pyramid.view import view_config
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


@view_config(route_name='home', renderer='templates/index.pt')
def index(context, request):
    r = request.registry.redis
    data = r.get(r.randomkey())

    if isinstance(data, basestring):
        data = json.loads(data)
    return {'data': data}
