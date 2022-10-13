# coding=utf-8

"""shortipy.services.url file."""

from click import STRING, option
from flask import Flask
from flask.cli import AppGroup

from shortipy.services.redis import redis_client

cli = AppGroup('urls', help='Manage URLs.')


def init_app(app: Flask) -> Flask:
    """Initializes the application URLs.

    :param app: The Flask application instance.
    :type app: Flask
    :return: The Flask application instance.
    :rtype: Flask
    """
    app.cli.add_command(cli)
    return app


@cli.command('set', help='Set URL by key.')
@option('-k', '--key', type=STRING, prompt='Enter the key', help='Specify the key.')
@option('-u', '--url', type=STRING, prompt='Enter the URL', help='Specify the URL.')
def set_url(key: str, url: str):
    """Set URL by key.

    :param key; Key.
    :type key: str
    :param url: URL.
    :type url: str
    """
    print(f'Setting {key}...')
    redis_client.set(key, url)
    print('Done.')


@cli.command('del', help='Delete URL by key.')
@option('-k', '--key', type=STRING, prompt='Enter the key', help='Specify the key.')
def del_url(key: str):
    """Delete URL by key.

    :param key; Key.
    :type key: str
    """
    print(f'Deleting {key}...')
    redis_client.delete(key)
    print('Done.')
