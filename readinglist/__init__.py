"""Main entry point
"""
from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("readinglist.views")
    config.scan("readinglist.auth")
    return config.make_wsgi_app()
