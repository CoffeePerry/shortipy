# coding=utf-8

"""shortipy.controllers.api.url file."""

from flask import Flask, Blueprint, request, abort
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import use_args
from marshmallow.validate import Length

from shortipy.services.exceptions import MethodVersionNotFound
from shortipy.services.serialization import marshmallow
from shortipy.services.url import get_urls, get_url_value, insert_url, update_url


class UrlSchema(marshmallow.Schema):
    """Class to define url schema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class Meta."""

        ordered = True
        fields = ('key', 'value', 'links')

    links = marshmallow.Hyperlinks(  # pylint: disable=no-member
        {
            'self': marshmallow.URLFor('api.url', values=dict(key='<key>'))  # pylint: disable=no-member
        }
    )


class UrlListAPI(MethodView):
    """Urls list API."""

    init_every_request = False

    def __init__(self):
        """UrlListAPI constructor."""
        self.url_schema = UrlSchema()
        self.urls_schema = UrlSchema(many=True)

    def get(self):
        """Get urls.

        :return: All urls.
        :rtype: dict[str, str]
        """
        if request.headers.get('Accept-Version', '1.0') == '1.0':
            urls = get_urls()
            if len(urls) < 1:
                abort(404)
            return {'urls': self.urls_schema.dump([{'key': key, 'value': value} for key, value in urls.items()])}
        raise MethodVersionNotFound()

    @use_args({'value': fields.Str(required=True, validate=Length(min=1))}, location='json')
    def post(self, args: dict):
        """Post url.

        :param args: Arguments.
        :type args: dict
        :return: Inserted url.
        :rtype: dict[str, str]
        """
        if request.headers.get('Accept-Version', '1.0') == '1.0':
            return {'url': self.url_schema.dump({'key': insert_url(args['value']), 'value': args['value']})}, 201
        raise MethodVersionNotFound()


class UrlAPI(MethodView):
    """Url API."""

    init_every_request = False

    def __init__(self):
        """UrlAPI constructor."""
        self.url_schema = UrlSchema()

    def get(self, key: str):
        """Get url.

        :param key: Url key.
        :type key: str
        :return: Url.
        :rtype: dict[str, str]
        """
        if request.headers.get('Accept-Version', '1.0') == '1.0':
            value = get_url_value(key)
            if value is None:
                abort(404)
            return {'url': self.url_schema.dump({'key': key, 'value': value})}
        raise MethodVersionNotFound()

    @use_args({'value': fields.Str(required=True, validate=Length(min=1))}, location='json')
    def put(self, args: dict, key: str):
        """Put url.

        :param args: Arguments.
        :type args: dict
        :param key: Url key.
        :type key: str
        :return: Updated url.
        :rtype: dict[str, str]
        """
        if request.headers.get('Accept-Version', '1.0') == '1.0':
            value = update_url(key, args['value'])
            if value is None:
                abort(404)
            return {'url': self.url_schema.dump({'key': key, 'value': value})}
        raise MethodVersionNotFound()


def register_api(app: Flask | Blueprint) -> Flask | Blueprint:
    """Register API.

    :param app: The Flask (or Blueprint) application instance.
    :type app: Flask | Blueprint
    :return: The Flask (or Blueprint) application instance.
    :rtype: Flask | Blueprint
    """
    app.add_url_rule('/urls/', view_func=UrlListAPI.as_view('urls'))
    app.add_url_rule('/urls/<key>', view_func=UrlAPI.as_view('url'))
    return app
