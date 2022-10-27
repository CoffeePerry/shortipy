# coding=utf-8

"""tests.test_resolution file."""

from flask.testing import FlaskClient

from tests import URL_KEY_TEST, URL_KEY_TEST_WRONG, URL_VALUE_TEST


def test_resolve(client: FlaskClient):
    """Test resolve.

    :param client: Flask Client.
    :type client: FlaskClient
    """
    response = client.get(f'/{URL_KEY_TEST}')  # follow_redirects=True
    assert response.status_code == 302
    # assert len(response.history) == 1
    # assert response.request.path == URL_TEST
    assert response.headers['Location'] == URL_VALUE_TEST

    response_wrong = client.get(f'/{URL_KEY_TEST_WRONG}')  # follow_redirects=True
    assert response_wrong.status_code == 404
    # assert len(response_wrong.history) == 0
