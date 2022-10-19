# coding=utf-8

"""shortipy.controllers.api.url file."""

from flask import request
from flask_restful import Resource, marshal

from shortipy.services.exceptions import MethodVersionNotFound
from shortipy.services.url import url_fields, get_request_parser, get_urls


class UrlListAPI(Resource):
    """Urls list API."""

    def __init__(self):
        """UrlListAPI constructor."""
        self.reqparse = get_request_parser()
        super().__init__()

    @staticmethod
    def get():
        """Get urls.

        :return: All urls.
        """
        if request.headers.get('Accept-Version', '1.0') == '1.0':
            return {'urls': [marshal(url, url_fields) for url in get_urls()]}
        raise MethodVersionNotFound()
