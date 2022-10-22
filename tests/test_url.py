# coding=utf-8

"""tests.test_url file."""

from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

from shortipy.services.redis import redis_client
from shortipy.services.url import generate_key

from tests import URL_TEST_CLI, KEY_TEST, URL_TEST

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
        ValueStorage.key_cli = result.output[-8:-2]
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

    @staticmethod
    def test_url_list_api_get(client: FlaskClient):
        """Test UrlListAPI.

        :param client: Flask Client.
        :type client: FlaskClient
        """
        response = client.get('/api/urls/')
        assert response.status_code == 200
        assert len(response.json['urls']) > 0
        assert response.json['urls'][0]['key'] != ''
        assert response.json['urls'][0]['value'] != ''
        assert '/urls/' in response.json['urls'][0]['links']['self']

    @staticmethod
    def test_url_api_get(client: FlaskClient):
        """Test UrlAPI.

        :param client: Flask Client.
        :type client: FlaskClient
        """
        response = client.get(f'/api/urls/{KEY_TEST}')
        assert response.status_code == 200
        assert response.json['url']['key'] == KEY_TEST
        assert response.json['url']['value'] == URL_TEST
        assert response.json['url']['links']['self'] == f'/api/urls/{KEY_TEST}'
