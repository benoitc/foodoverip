from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from velruse.providers import twitter

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
    config.include(twitter)

    config.add_route('home', '/')

    config.scan('.views')
    return config.make_wsgi_app()

