# coding=utf-8

"""tests.conftest file."""

from typing import Generator

from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from pytest import fixture

from shortipy import create_app
from shortipy.services.redis import redis_client

from tests import URL_KEY_TEST, URL_VALUE_TEST


@fixture
def application() -> Generator[Flask, None, None]:
    """Get the Flask application's generator from factory.

    :return: Flask application's generator.
    :rtype: Generator[Flask, None, None]
    """
    __app = create_app({
        'TESTING': True,
        'SECRET_KEY': b'test',
        'REDIS_URL': 'redis://127.0.0.1:6379/0'
    })
    with __app.app_context():
        redis_client.set(URL_KEY_TEST, URL_VALUE_TEST)
    try:
        yield __app
    finally:
        with __app.app_context():
            redis_client.delete(URL_KEY_TEST)


@fixture
def client(application: Flask) -> FlaskClient:  # pylint: disable=redefined-outer-name
    """Get Flask application client.

    :param application: Flask application.
    :type application: Flask
    :return: Flask Client.
    :rtype: FlaskClient
    """
    return application.test_client()


@fixture
def runner(application: Flask) -> FlaskCliRunner:  # pylint: disable=redefined-outer-name
    """Get Flask application CLI runner.

    :param application: Flask application.
    :type application: Flask
    :return: Flask CLI Runner.
    :rtype: FlaskCliRunner
    """
    return application.test_cli_runner()
