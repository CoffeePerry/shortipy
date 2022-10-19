# coding=utf-8

"""shortipy.services.url file."""

from string import ascii_lowercase
from os import linesep
from random import SystemRandom

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


def get_url(key: str) -> str | None:
    """Get URL by passed key.

    :param key: Key to find.
    :type key: str
    :return: URL found or None.
    :rtype: str | None
    """
    return redis_client.get(key)


def insert_url(url: str) -> str:
    """Insert passed URL and generate a key to retrieve it.

    :param url: URL to insert.
    :type url: str
    :return: key to retrieve the URL.
    :rtype: str
    """
    key = None
    while True:
        key = generate_key()
        result = redis_client.set(key, url, nx=True)
        if result is not None:
            break
    return key


def generate_key() -> str:
    """Generate new key.

    :return: A new key.
    :rtype: str
    """
    return ''.join(SystemRandom().choice(ascii_lowercase) for _ in range(6))


@cli.command('new', help='Insert new URL.')
@option('-u', '--url', type=STRING, prompt='Enter the URL', help='Specify the URL.')
def new_url(url: str):
    """Insert new URL.

    :param url: URL.
    :type url: str
    """
    print(f'Insert URL: {url}...')
    key = insert_url(url)
    if key is None:
        print('Error: unable to generate a valid key.')
    print(f'Done.{linesep}Use the following key to retrieve it: {key}.')


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
