# coding=utf-8

"""shortipy.services.url file."""

from string import ascii_lowercase
from os import linesep
from random import SystemRandom

from click import STRING, option
from flask import Flask
from flask.cli import AppGroup

from shortipy.services.redis import redis_client

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
    return {key: get_url_value(key) for key in redis_client.keys('*')}


def get_url_value(key: str) -> str | None:
    """Get url value by passed key.

    :param key: Key to find.
    :type key: str
    :return: Url value found or None.
    :rtype: str | None
    """
    return redis_client.get(key)


def insert_url(value: str) -> str:
    """Insert passed url value and generate a key to retrieve it.

    :param value: Url value to insert.
    :type value: str
    :return: Key to retrieve the url.
    :rtype: str
    """
    while True:
        key = generate_key()
        result = redis_client.set(key, value, nx=True)
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
    url_value = redis_client.get(key)
    if url_value is not None:
        redis_client.set(key, value)
        url_value = value
    return url_value
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
    print(f'Deleting {key}...')
    redis_client.delete(key)
    print('Done.')
# endregion
