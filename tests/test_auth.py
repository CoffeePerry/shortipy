# coding=utf-8

"""tests.test_auth file."""

from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient
from pytest import raises

from shortipy.services.exceptions import MethodVersionNotFound
from shortipy.services.redis import redis_client
from shortipy.services.auth import USER_KEYS_DOMAIN, insert_user, delete_user, normalize_input

from tests import USER_USERNAME, USER_PASSWORD, USER_PASSWORD_WRONG


class Auth:
    """Auth class."""

    def __init__(self, application: Flask, client: FlaskClient):
        """Auth constructor.

        :param application: Flask application.
        :type application: Flask
        :param client: Flask Client.
        :type client: FlaskClient
        """
        self.application = application
        self.client = client

    def __enter__(self) -> str:
        """Auth enter.

        :return: Access token.
        :rtype: str
        """
        with self.application.app_context():
            insert_user(USER_USERNAME, USER_PASSWORD)
        response = self.client.post('/api/auth/', json={'username': USER_USERNAME, 'password': USER_PASSWORD})
        return response.json['auth']['access_token']

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auth exit.

        :param exc_type: Exception type.
        :param exc_val: Exception value.
        :param exc_tb: Exception traceback.
        """
        with self.application.app_context():
            redis_client.delete(f'{USER_KEYS_DOMAIN}:{USER_USERNAME}')


def test_insert_user_wrong_duplicate(application: Flask):
    """Test insert user wrong: duplicate user.

    :param application: Flask application.
    :type application: Flask
    """
    with application.app_context():
        redis_client.flushdb()
        insert_user(USER_USERNAME, USER_PASSWORD)
        try:
            with raises(Exception, match=f'User "{USER_USERNAME}" already exists'):
                insert_user(USER_USERNAME, USER_PASSWORD)
        finally:
            redis_client.delete(f'{USER_KEYS_DOMAIN}:{USER_USERNAME}')


def test_delete_user_wrong_duplicate(application: Flask):
    """Test delete user wrong: user not found.

    :param application: Flask application.
    :type application: Flask
    """
    with application.app_context():
        redis_client.flushdb()
        with raises(Exception, match=f'User "{USER_USERNAME}" not found'):
            delete_user(USER_USERNAME)


def test_normalize_input_wrong_invalid_input(application: Flask):
    """Test normalize input wrong: invalid input.

    :param application: Flask application.
    :type application: Flask
    """
    with application.app_context():
        with raises(Exception, match='Invalid value'):
            normalize_input(None)


def test_new_user(application: Flask, runner: FlaskCliRunner):
    """Test CLI new user.

    :param application: Flask application.
    :type application: Flask
    :param runner: Flask CLI Runner.
    :type runner: FlaskCliRunner
    """
    result = runner.invoke(args=['users', 'new', '-u', USER_USERNAME, '-p', USER_PASSWORD])
    assert f'Insert user: {USER_USERNAME}...' in result.output
    assert 'Done.' in result.output
    try:
        with application.app_context():
            assert redis_client.hget(f'{USER_KEYS_DOMAIN}:{USER_USERNAME}', 'password') is not None
    finally:
        with application.app_context():
            delete_user(USER_USERNAME)


def test_del_user(application: Flask, runner: FlaskCliRunner):
    """Test CLI del user.

    :param application: Flask application.
    :type application: Flask
    :param runner: Flask CLI Runner.
    :type runner: FlaskCliRunner
    """
    with application.app_context():
        insert_user(USER_USERNAME, USER_PASSWORD)
    try:
        runner.invoke(args=['users', 'del', '-u', USER_USERNAME])
        with application.app_context():
            assert not redis_client.hgetall(f'{USER_KEYS_DOMAIN}:{USER_USERNAME}')
    finally:
        with application.app_context():
            redis_client.delete(f'{USER_KEYS_DOMAIN}:{USER_USERNAME}')


def test_auth_list_api_post_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test AuthListAPI POST wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/auth/', headers={'Accept-Version': 'x.y'}, json={
        'username': USER_USERNAME, 'password': USER_PASSWORD
    })
    with application.app_context():
        assert response.status_code == MethodVersionNotFound.code


def test_auth_list_api_post_wrong_missing(client: FlaskClient):
    """Test AuthListAPI POST wrong: missing value.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/auth/')
    assert response.status_code == 422


def test_auth_list_api_post_wrong_empty_username(client: FlaskClient):
    """Test AuthListAPI POST wrong: empty username value.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/auth/', json={'username': '', 'password': USER_PASSWORD})
    assert response.status_code == 422


def test_auth_list_api_post_wrong_empty_password(client: FlaskClient):
    """Test AuthListAPI POST wrong: empty password value.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/auth/', json={'username': USER_USERNAME, 'password': ''})
    assert response.status_code == 422


def test_auth_list_api_post_wrong_unauthorized(application: Flask, client: FlaskClient):
    """Test AuthListAPI POST wrong: unauthorized.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        insert_user(USER_USERNAME, USER_PASSWORD)
    try:
        response = client.post('/api/auth/', json={'username': USER_USERNAME, 'password': USER_PASSWORD_WRONG})
        assert response.status_code == 401
    finally:
        with application.app_context():
            redis_client.delete(f'{USER_KEYS_DOMAIN}:{USER_USERNAME}')


def test_auth_list_api_post(application: Flask, client: FlaskClient):
    """Test AuthListAPI POST.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        insert_user(USER_USERNAME, USER_PASSWORD)
    try:
        response = client.post('/api/auth/', json={'username': USER_USERNAME, 'password': USER_PASSWORD})
        assert response.status_code == 200
        assert response.json['auth']['username'] == USER_USERNAME
        assert response.json['auth']['access_token'] != ''
    finally:
        with application.app_context():
            redis_client.delete(f'{USER_KEYS_DOMAIN}:{USER_USERNAME}')
