import json
import redis


class JSONEncoder(json.JSONEncoder):
    """Subclass of the default encoder to support custom objects"""
    def default(self, o):
        if hasattr(o, "_to_serialize"):
            # build up the object
            data = {}
            for attr in o._to_serialize:
                data[attr] = getattr(o, attr)
            return data
        elif hasattr(o, "isoformat"):
            return o.isoformat()
        else:
            return json.JSONEncoder.default(self, o)


def get_connections():
    con = {}
    for idx, name in enumerate(('tweets', 'tags', 'users')):
        con[name] = redis.Redis(connection_pool=redis.ConnectionPool(
                        host='localhost', port=6379, db=idx))

    return con
