# coding=utf-8

"""shortipy.services.url file."""

from typing import Final
from string import ascii_lowercase
from os import linesep
from random import SystemRandom

from click import STRING, option
from flask import Flask
from flask.cli import AppGroup
from werkzeug.exceptions import NotFound

from shortipy.services.redis import redis_client

URL_KEYS_DOMAIN: Final = 'url'

cli = AppGroup('urls', help='Manage urls.')


def init_app(app: Flask) -> Flask:
    """Initializes the application urls.

    :param app: The Flask application instance.
    :type app: Flask
    :return: The Flask application instance.
    :rtype: Flask
    """
    app.cli.add_command(cli)
    return app


# region CRUD functions
def get_urls() -> dict[str, str]:
    """Get urls.

    :return: Dictionary of urls (keys and values).
    :rtype: dict[str, str]
    """
    return {key.removeprefix(f'{URL_KEYS_DOMAIN}:'): redis_client.get(key)
            for key in redis_client.keys(f'{URL_KEYS_DOMAIN}:*')}


def get_url_value(key: str) -> str | None:
    """Get url value by passed key.

    :param key: Key to find.
    :type key: str
    :return: Url value found or None.
    :rtype: str | None
    """
    return redis_client.get(f'{URL_KEYS_DOMAIN}:{key}')


def insert_url(value: str) -> str:
    """Insert passed url value and generate a key to retrieve it.

    :param value: Url value to insert.
    :type value: str
    :return: Key to retrieve the url.
    :rtype: str
    """
    while True:
        key = generate_key()
        result = redis_client.set(f'{URL_KEYS_DOMAIN}:{key}', value, nx=True)
        if result is not None:
            break
    return key


def update_url(key: str, value: str | None) -> str:
    """Update url by passed key and value.

    :param key: Key to find.
    :type key: str
    :param value: Url value to update.
    :type value: str
    :return: New url value or None if no key found.
    :rtype: str | None
    """
    url_value = get_url_value(key)
    if url_value is None:
        raise NotFound('Url not found')

    redis_client.set(f'{URL_KEYS_DOMAIN}:{key}', value)
    return value


def delete_url(key: str):
    """Delete url by passed key.

    :param key: Url key to delete.
    :type key: str
    """
    if get_url_value(key) is None:
        raise NotFound('Url not found')

    return redis_client.delete(f'{URL_KEYS_DOMAIN}:{key}')
# endregion


# region Other functions
def generate_key() -> str:
    """Generate new key.

    :return: New key.
    :rtype: str
    """
    return ''.join(SystemRandom().choice(ascii_lowercase) for _ in range(6))
# endregion


# region CLI functions
@cli.command('new', help='Insert new url.')
@option('-u', '--url', type=STRING, prompt='Enter the url', help='Specify the url.')
def new_url(url: str):
    """Insert new url.

    :param url: Url value.
    :type url: str
    """
    print(f'Insert url: {url}...')
    key = insert_url(url)
    print(f'Done.{linesep}Use the following key to retrieve it: {key}.')


@cli.command('del', help='Delete url by key.')
@option('-k', '--key', type=STRING, prompt='Enter the key', help='Specify the key.')
def del_url(key: str):
    """Delete url by key.

    :param key; Key.
    :type key: str
    """
    print(f'Deleting url: {key}...')
    delete_url(key)
    print('Done.')
# endregion
