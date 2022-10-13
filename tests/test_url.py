# coding=utf-8

"""tests.test_url file."""

from flask import Flask
from flask.testing import FlaskCliRunner

from shortipy.services.redis import redis_client

from tests import KEY_TEST_CLI, URL_TEST_CLI


class TestURL:
    """Test URL."""

    @staticmethod
    def test_set_url(application: Flask, runner: FlaskCliRunner):
        """Test CLI set url.

        :param application: Flask application.
        :type application: Flask
        :param runner: Flask CLI Runner.
        :type runner: FlaskCliRunner
        """
        runner.invoke(args=['urls', 'set', '-k', KEY_TEST_CLI, '-u', URL_TEST_CLI])
        with application.app_context():
            assert redis_client.get(KEY_TEST_CLI) == URL_TEST_CLI

    @staticmethod
    def test_del_url(application: Flask, runner: FlaskCliRunner):
        """Test CLI del url.

        :param application: Flask application.
        :type application: Flask
        :param runner: Flask CLI Runner.
        :type runner: FlaskCliRunner
        """
        runner.invoke(args=['urls', 'del', '-k', KEY_TEST_CLI])
        with application.app_context():
            assert redis_client.get(KEY_TEST_CLI) is None
