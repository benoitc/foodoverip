from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from velruse.providers import twitter
import redis

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
"""
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['cookie.secret'],
    )
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
    )

    config.add_static_view(name='static', path='foodoverip:/static')

    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    setattr(config.registry, 'redis', redis.Redis(connection_pool=pool))
    config.include(twitter)

    config.add_route('home', '/')

    config.scan('.views')
    return config.make_wsgi_app()



