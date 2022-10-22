# coding=utf-8

"""shortipy.controllers.api module."""

from flask import Blueprint
from flask_restful import Api

from shortipy.controllers.api.url import UrlListAPI

api_blueprint = Blueprint('api', __name__, url_prefix='/api')


def init_api(api: Api) -> Api:
    """Initializes the application API: load routes.

    :param api: The Flask application's API instance.
    :type api: Api
    :return: The Flask application's API instance.
    :rtype: Api
    """
    if len(api.resources) < 1:
        api.add_resource(UrlListAPI, '/urls/', endpoint='urls')
        # api.add_resource(UrlAPI, '/url/<int:id>', endpoint='url')
    return api
