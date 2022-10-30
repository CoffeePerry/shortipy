# coding=utf-8

"""tests.test_url file."""

from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

from shortipy.services.exceptions import MethodVersionNotFound
from shortipy.services.redis import redis_client
from shortipy.services.url import insert_url, delete_url

from tests import URL_KEY_TEST, URL_VALUE_TEST, URL_VALUE_BIS_TEST


def test_new_url(application: Flask, runner: FlaskCliRunner):
    """Test CLI new url.

    :param application: Flask application.
    :type application: Flask
    :param runner: Flask CLI Runner.
    :type runner: FlaskCliRunner
    """
    result = runner.invoke(args=['urls', 'new', '-u', URL_VALUE_TEST])
    url_key = result.output[-8:-2]
    try:
        with application.app_context():
            assert redis_client.get(url_key) == URL_VALUE_TEST
    finally:
        with application.app_context():
            delete_url(url_key)


def test_del_url(application: Flask, runner: FlaskCliRunner):
    """Test CLI del url.

    :param application: Flask application.
    :type application: Flask
    :param runner: Flask CLI Runner.
    :type runner: FlaskCliRunner
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        runner.invoke(args=['urls', 'del', '-k', url_key])
        with application.app_context():
            assert redis_client.get(url_key) is None
    finally:
        with application.app_context():
            redis_client.delete(url_key)


def test_url_list_api_get_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlListAPI GET wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.get('/api/urls/', headers={'Accept-Version': 'x.y'})
    with application.app_context():
        assert response.status_code == MethodVersionNotFound.code


def test_url_list_api_get_404(application: Flask, client: FlaskClient):
    """Test UrlListAPI GET: error 404.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        redis_client.flushdb()
    response = client.get('/api/urls/')
    assert response.status_code == 404


def test_url_api_get_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlAPI GET wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.get(f'/api/urls/{url_key}', headers={'Accept-Version': 'x.y'})
        with application.app_context():
            assert response.status_code == MethodVersionNotFound.code
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_get_404(application: Flask, client: FlaskClient):
    """Test UrlAPI GET: error 404.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        redis_client.flushdb()
    response = client.get(f'/api/urls/{URL_KEY_TEST}')
    assert response.status_code == 404


def test_url_list_api_post_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlListAPI POST wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/urls/', headers={'Accept-Version': 'x.y'}, json={'value': URL_VALUE_TEST})
    with application.app_context():
        assert response.status_code == MethodVersionNotFound.code


def test_url_list_api_post_wrong_missing(client: FlaskClient):
    """Test UrlListAPI POST wrong: missing value.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/urls/')
    assert response.status_code == 422


def test_url_list_api_post_wrong_empty(client: FlaskClient):
    """Test UrlListAPI POST wrong: empty value.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/urls/', json={'value': ''})
    assert response.status_code == 422


def test_url_list_api_post(application: Flask, client: FlaskClient):
    """Test UrlListAPI POST.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    url_key = ''
    try:
        response = client.post('/api/urls/', json={'value': URL_VALUE_TEST})
        assert response.status_code == 201
        url_key = response.json['url']['key']
        assert response.json['url']['key'] == url_key
        assert response.json['url']['value'] == URL_VALUE_TEST
        assert response.json['url']['links']['self'] == f'/api/urls/{url_key}'
        with application.app_context():
            assert redis_client.get(url_key) == URL_VALUE_TEST
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_list_api_get(application: Flask, client: FlaskClient):
    """Test UrlListAPI GET.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        redis_client.flushdb()
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.get('/api/urls/')
        assert response.status_code == 200
        assert len(response.json['urls']) == 1
        assert response.json['urls'][0]['key'] == url_key
        assert response.json['urls'][0]['value'] == URL_VALUE_TEST
        assert response.json['urls'][0]['links']['self'] == f'/api/urls/{url_key}'
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_get(application: Flask, client: FlaskClient):
    """Test UrlAPI GET.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.get(f'/api/urls/{url_key}')
        assert response.status_code == 200
        assert response.json['url']['key'] == url_key
        assert response.json['url']['value'] == URL_VALUE_TEST
        assert response.json['url']['links']['self'] == f'/api/urls/{url_key}'
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_put_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlAPI PUT wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.put(
            f'/api/urls/{url_key}', headers={'Accept-Version': 'x.y'}, json={'value': URL_VALUE_TEST}
        )
        with application.app_context():
            assert response.status_code == MethodVersionNotFound.code
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_put_wrong_missing(application: Flask, client: FlaskClient):
    """Test UrlAPI PUT wrong: missing value.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.put(f'/api/urls/{url_key}')
        assert response.status_code == 422
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_put_wrong_empty(application: Flask, client: FlaskClient):
    """Test UrlAPI PUT wrong: empty value.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.put(f'/api/urls/{url_key}', json={'value': ''})
        assert response.status_code == 422
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_put_wrong_404(application: Flask, client: FlaskClient):
    """Test UrlAPI PUT wrong: not found (404).

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        redis_client.flushdb()
    response = client.put(f'/api/urls/{URL_KEY_TEST}', json={'value': URL_VALUE_TEST})
    assert response.status_code == 404


def test_url_api_put(application: Flask, client: FlaskClient):
    """Test UrlAPI PUT.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.put(f'/api/urls/{url_key}', json={'value': URL_VALUE_BIS_TEST})
        assert response.status_code == 200
        assert response.json['url']['key'] == url_key
        assert response.json['url']['value'] == URL_VALUE_BIS_TEST
        assert response.json['url']['links']['self'] == f'/api/urls/{url_key}'
        with application.app_context():
            assert redis_client.get(url_key) == URL_VALUE_BIS_TEST
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_delete_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlAPI DELETE wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.delete(f'/api/urls/{URL_KEY_TEST}', headers={'Accept-Version': 'x.y'})
    with application.app_context():
        assert response.status_code == MethodVersionNotFound.code


def test_url_api_delete_wrong_missing(application: Flask, client: FlaskClient):
    """Test UrlAPI DELETE wrong: missing value.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        redis_client.flushdb()
    response = client.delete(f'/api/urls/{URL_KEY_TEST}')
    assert response.status_code == 404


def test_url_api_delete(application: Flask, client: FlaskClient):
    """Test UrlAPI DELETE.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.delete(f'/api/urls/{url_key}')
        assert response.status_code == 204
        with application.app_context():
            assert redis_client.get(url_key) is None
    finally:
        with application.app_context():
            redis_client.delete(url_key)
