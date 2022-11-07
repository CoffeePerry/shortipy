# coding=utf-8

"""tests.test_url file."""

from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

from shortipy.services.exceptions import MethodVersionNotFound
from shortipy.services.redis import redis_client
from shortipy.services.url import URL_KEYS_DOMAIN, insert_url, delete_url

from tests import URL_KEY_TEST, URL_VALUE_TEST, URL_VALUE_BIS_TEST
from tests.test_auth import Auth


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
            assert redis_client.get(f'{URL_KEYS_DOMAIN}:{url_key}') == URL_VALUE_TEST
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
            assert redis_client.get(f'{URL_KEYS_DOMAIN}:{url_key}') is None
    finally:
        with application.app_context():
            redis_client.delete(f'{URL_KEYS_DOMAIN}:{url_key}')


def test_url_list_api_get_wrong_unauthorized(application: Flask, client: FlaskClient):
    """Test UrlListAPI GET wrong: unauthorized.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        redis_client.flushdb()
    response = client.get('/api/urls/')
    assert response.status_code == 401


def test_url_list_api_get_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlListAPI GET wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with Auth(application, client) as access_token:
        response = client.get('/api/urls/', headers={
            'Authorization': f'Bearer {access_token}',
            'Accept-Version': 'x.y'
        })
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
    with Auth(application, client) as access_token:
        response = client.get('/api/urls/', headers={'Authorization': f'Bearer {access_token}'})
        assert response.status_code == 404


def test_url_api_get_wrong_unauthorized(application: Flask, client: FlaskClient):
    """Test UrlAPI GET wrong: unauthorized.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        redis_client.flushdb()
    response = client.get(f'/api/urls/{URL_KEY_TEST}')
    assert response.status_code == 401


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
        with Auth(application, client) as access_token:
            response = client.get(f'/api/urls/{url_key}', headers={
                'Authorization': f'Bearer {access_token}',
                'Accept-Version': 'x.y'
            })
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
    with Auth(application, client) as access_token:
        response = client.get(f'/api/urls/{URL_KEY_TEST}', headers={'Authorization': f'Bearer {access_token}'})
        assert response.status_code == 404


def test_url_list_api_post_unauthorized(client: FlaskClient):
    """Test UrlListAPI POST wrong: unauthorized.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.post('/api/urls/', json={'value': URL_VALUE_TEST})
    assert response.status_code == 401


def test_url_list_api_post_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlListAPI POST wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with Auth(application, client) as access_token:
        response = client.post('/api/urls/', headers={
            'Authorization': f'Bearer {access_token}',
            'Accept-Version': 'x.y'
        }, json={'value': URL_VALUE_TEST})
        with application.app_context():
            assert response.status_code == MethodVersionNotFound.code


def test_url_list_api_post_wrong_missing(application: Flask, client: FlaskClient):
    """Test UrlListAPI POST wrong: missing value.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with Auth(application, client) as access_token:
        response = client.post('/api/urls/', headers={'Authorization': f'Bearer {access_token}'})
        assert response.status_code == 422


def test_url_list_api_post_wrong_empty(application: Flask, client: FlaskClient):
    """Test UrlListAPI POST wrong: empty value.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with Auth(application, client) as access_token:
        response = client.post('/api/urls/', headers={'Authorization': f'Bearer {access_token}'}, json={'value': ''})
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
        with Auth(application, client) as access_token:
            response = client.post('/api/urls/', headers={'Authorization': f'Bearer {access_token}'},
                                   json={'value': URL_VALUE_TEST})
            assert response.status_code == 201
            url_key = response.json['url']['key']
            assert response.json['url']['key'] == url_key
            assert response.json['url']['value'] == URL_VALUE_TEST
            assert response.json['url']['links']['self'] == f'/api/urls/{url_key}'
            with application.app_context():
                assert redis_client.get(f'{URL_KEYS_DOMAIN}:{url_key}') == URL_VALUE_TEST
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
        with Auth(application, client) as access_token:
            response = client.get('/api/urls/', headers={'Authorization': f'Bearer {access_token}'})
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
        with Auth(application, client) as access_token:
            response = client.get(f'/api/urls/{url_key}', headers={'Authorization': f'Bearer {access_token}'})
            assert response.status_code == 200
            assert response.json['url']['key'] == url_key
            assert response.json['url']['value'] == URL_VALUE_TEST
            assert response.json['url']['links']['self'] == f'/api/urls/{url_key}'
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_put_wrong_unauthorized(application: Flask, client: FlaskClient):
    """Test UrlAPI PUT wrong: unauthorized.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with application.app_context():
        url_key = insert_url(URL_VALUE_TEST)
    try:
        response = client.put(f'/api/urls/{url_key}', json={'value': URL_VALUE_TEST})
        assert response.status_code == 401
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
        with Auth(application, client) as access_token:
            response = client.put(
                f'/api/urls/{url_key}', headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept-Version': 'x.y'
                }, json={'value': URL_VALUE_TEST}
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
        with Auth(application, client) as access_token:
            response = client.put(f'/api/urls/{url_key}', headers={'Authorization': f'Bearer {access_token}'})
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
        with Auth(application, client) as access_token:
            response = client.put(f'/api/urls/{url_key}', headers={'Authorization': f'Bearer {access_token}'},
                                  json={'value': ''})
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
    with Auth(application, client) as access_token:
        response = client.put(f'/api/urls/{URL_KEY_TEST}', headers={'Authorization': f'Bearer {access_token}'},
                              json={'value': URL_VALUE_TEST})
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
        with Auth(application, client) as access_token:
            response = client.put(f'/api/urls/{url_key}', headers={'Authorization': f'Bearer {access_token}'},
                                  json={'value': URL_VALUE_BIS_TEST})
            assert response.status_code == 200
            assert response.json['url']['key'] == url_key
            assert response.json['url']['value'] == URL_VALUE_BIS_TEST
            assert response.json['url']['links']['self'] == f'/api/urls/{url_key}'
            with application.app_context():
                assert redis_client.get(f'{URL_KEYS_DOMAIN}:{url_key}') == URL_VALUE_BIS_TEST
    finally:
        with application.app_context():
            delete_url(url_key)


def test_url_api_delete_wrong_unauthorized(client: FlaskClient):
    """Test UrlAPI DELETE wrong: unauthorized.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.delete(f'/api/urls/{URL_KEY_TEST}')
    assert response.status_code == 401


def test_url_api_delete_wrong_method_version_not_found(application: Flask, client: FlaskClient):
    """Test UrlAPI DELETE wrong: method version not found.

    :param application: Flask application.
    :type application: Flask
    :param client: Flask Client.
    :type client: FlaskClient
    """
    with Auth(application, client) as access_token:
        response = client.delete(f'/api/urls/{URL_KEY_TEST}', headers={
            'Authorization': f'Bearer {access_token}',
            'Accept-Version': 'x.y'
        })
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
    with Auth(application, client) as access_token:
        response = client.delete(f'/api/urls/{URL_KEY_TEST}', headers={'Authorization': f'Bearer {access_token}'})
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
        with Auth(application, client) as access_token:
            response = client.delete(f'/api/urls/{url_key}', headers={'Authorization': f'Bearer {access_token}'})
            assert response.status_code == 204
            with application.app_context():
                assert redis_client.get(f'{URL_KEYS_DOMAIN}:{url_key}') is None
    finally:
        with application.app_context():
            redis_client.delete(f'{URL_KEYS_DOMAIN}:{url_key}')
