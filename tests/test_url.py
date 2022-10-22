# coding=utf-8

"""tests.test_url file."""

from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

from shortipy.services.redis import redis_client
from shortipy.services.url import generate_key

from tests import URL_VALUE_TEST_CLI, URL_KEY_TEST, URL_VALUE_TEST

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
        result = runner.invoke(args=['urls', 'new', '-u', URL_VALUE_TEST_CLI])
        ValueStorage.url_key_cli = result.output[-8:-2]
        with application.app_context():
            assert redis_client.get(ValueStorage.url_key_cli) == URL_VALUE_TEST_CLI

    def test_del_url(self, application: Flask, runner: FlaskCliRunner):
        """Test CLI del url.

        :param application: Flask application.
        :type application: Flask
        :param runner: Flask CLI Runner.
        :type runner: FlaskCliRunner
        """
        if ValueStorage.url_key_cli:
            with application.app_context():
                ValueStorage.url_key_cli = generate_key()
        runner.invoke(args=['urls', 'del', '-k', ValueStorage.url_key_cli])
        with application.app_context():
            assert redis_client.get(ValueStorage.url_key_cli) is None

    @staticmethod
    def test_url_list_api_get_404(client: FlaskClient):
        """Test UrlListAPI GET: error 404.

        :param client: Flask Client.
        :type client: FlaskClient
        """
        response = client.get('/api/urls/')
        assert response.status_code == 404

    @staticmethod
    def test_url_api_get_404(client: FlaskClient):
        """Test UrlAPI GET: error 404.

        :param client: Flask Client.
        :type client: FlaskClient
        """
        response = client.get(f'/api/urls/{URL_KEY_TEST}')
        assert response.status_code == 404

    @staticmethod
    def test_url_list_api_post(client: FlaskClient):
        """Test UrlListAPI POST.

        :param client: Flask Client.
        :type client: FlaskClient
        """
        response = client.post('/api/urls/', json={'value': URL_VALUE_TEST})
        assert response.status_code == 201
        assert response.json['url']['key'] != ''
        ValueStorage.url_key_client = response.json['url']['key']
        assert response.json['url']['value'] == URL_VALUE_TEST
        ValueStorage.url_value_client = response.json['url']['value']
        assert response.json['url']['links']['self'] == f'/api/urls/{ValueStorage.url_key_client}'

    @staticmethod
    def test_url_list_api_get(client: FlaskClient):
        """Test UrlListAPI GET.

        :param client: Flask Client.
        :type client: FlaskClient
        """
        response = client.get('/api/urls/')
        assert response.status_code == 200
        assert len(response.json['urls']) == 1
        assert response.json['urls'][0]['key'] == ValueStorage.url_key_client
        assert response.json['urls'][0]['value'] == ValueStorage.url_value_client
        assert '/urls/' in response.json['urls'][0]['links']['self']

    @staticmethod
    def test_url_api_get(client: FlaskClient):
        """Test UrlAPI GET.

        :param client: Flask Client.
        :type client: FlaskClient
        """
        response = client.get(f'/api/urls/{ValueStorage.url_key_client}')
        assert response.status_code == 200
        assert response.json['url']['key'] == ValueStorage.url_key_client
        assert response.json['url']['value'] == ValueStorage.url_value_client
        assert response.json['url']['links']['self'] == f'/api/urls/{ValueStorage.url_key_client}'
