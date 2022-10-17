# coding=utf-8

"""shortipy module."""

from typing import Final
from os import linesep, path, makedirs

from flask import Flask

from shortipy.services.config import Config
from shortipy.services.redis import init_app as init_redis
from shortipy.services.url import init_app as init_url
from shortipy.services.api import init_app as init_api
from shortipy.controllers.resolution import resolution_blueprint
from shortipy.controllers.api import api_blueprint

VERSION: Final = '1.1.1'
CONFIG_FILENAME: Final = 'config.py'


def create_app(options: dict | None = None) -> Flask | None:
    """Application factory.

    :param options: Optional application options (default: None).
    :type: dict | None
    :return: An application instance.
    :rtype: Flask | None
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(Config())

    if not isinstance(options, dict | None):
        raise Exception('Invalid options')
    if (options is None) or (not options.get('TESTING')):
        if not path.isdir(app.instance_path):
            makedirs(app.instance_path)
            raise Exception(f'Directory not found, so just created: {app.instance_path}.{linesep}'
                            f'Put file "{CONFIG_FILENAME}" inside, please.')

        config_file = path.join(app.instance_path, CONFIG_FILENAME)
        if not path.isfile(config_file):
            raise Exception(f'Configuration file not found: {config_file}')
        app.config.from_pyfile(config_file)

        if app.config.get('SECRET_KEY') is None:
            raise Exception(f'Set variable SECRET_KEY with random string in file: {config_file}')

    if options is not None:
        app.config.from_mapping(options)

    init_url(init_redis(app))

    app.register_blueprint(resolution_blueprint)
    app.register_blueprint(init_api(api_blueprint))

    @app.cli.command('version', help='Display version.')
    def version():
        """Print Shortipy version."""
        print(f'Shortipy v{VERSION}')

    return app
