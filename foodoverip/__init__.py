from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from velruse.providers import twitter
from foodoverip.util import get_connections


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

    setattr(config.registry, 'con', get_connections())

    config.include(twitter)

    config.add_route('list', '/')
    config.add_route('random', '/random')
    config.add_route('about', '/about')
    config.add_view(route_name='about', renderer="templates/about.pt")

    config.add_route('tag', '/tag/{tag}')
    config.add_route('get', '/{key}')
    config.add_route('thumb', '/thumbs/square/{key}')

    config.add_route('user', '/user/{user}')

    config.scan('.views')

    config.add_subscriber('foodoverip.views.add_base_template',
                          'pyramid.events.BeforeRender')

    return config.make_wsgi_app()
