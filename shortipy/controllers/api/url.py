# coding=utf-8

"""shortipy.controllers.api.url file."""

from flask import request
from flask_restful import Resource

from shortipy.services.exceptions import MethodVersionNotFound


class UrlListAPI(Resource):
    """URLs list API."""

    def __init__(self):
        """UrlListAPI constructor."""
        # self.reqparse = services_url.get_request_parser()
        super().__init__()

    @staticmethod
    def get():
        """Get URLs.

        :return: All URLs.
        """
        if request.headers.get('Accept-Version', '1.0') == '1.0':
            pass
        raise MethodVersionNotFound()
