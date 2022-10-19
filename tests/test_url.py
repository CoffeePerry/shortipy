# coding=utf-8

"""tests.test_url file."""

from flask import Flask
from flask.testing import FlaskCliRunner

from shortipy.services.redis import redis_client
from shortipy.services.url import generate_key

from tests import URL_TEST_CLI

from tests.conftest import ValueStorage


class TestURL:
    """Test url."""

    def test_new_url(self, application: Flask, runner: FlaskCliRunner):
        """Test CLI new url.

        :param application: Flask application.
        :type application: Flask
        :param runner: Flask CLI Runner.
        :type runner: FlaskCliRunner
        """
        result = runner.invoke(args=['urls', 'new', '-u', URL_TEST_CLI])
        ValueStorage.key_cli = result.output[-7:-1]
        with application.app_context():
            assert redis_client.get(ValueStorage.key_cli) == URL_TEST_CLI

    def test_del_url(self, application: Flask, runner: FlaskCliRunner):
        """Test CLI del url.

        :param application: Flask application.
        :type application: Flask
        :param runner: Flask CLI Runner.
        :type runner: FlaskCliRunner
        """
        if ValueStorage.key_cli:
            with application.app_context():
                ValueStorage.key_cli = generate_key()
        runner.invoke(args=['urls', 'del', '-k', ValueStorage.key_cli])
        with application.app_context():
            assert redis_client.get(ValueStorage.key_cli) is None
