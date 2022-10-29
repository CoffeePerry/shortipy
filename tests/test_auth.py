# coding=utf-8

"""tests.test_auth file."""

from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

from shortipy.services.exceptions import MethodVersionNotFound
from shortipy.services.redis import redis_client
from shortipy.services.auth import insert_user, delete_user

from tests import USER_USERNAME, USER_PASSWORD


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
            assert redis_client.hget(f'user:{USER_USERNAME}') == USER_PASSWORD
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
            assert redis_client.hget(f'user:{USER_USERNAME}', 'password') is not None
    finally:
        with application.app_context():
            delete_user(USER_USERNAME)


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
        assert response.json['auth']['username'] == 'test'
        assert response.json['auth']['access_token'] != ''
    finally:
        with application.app_context():
            delete_user(USER_USERNAME)
