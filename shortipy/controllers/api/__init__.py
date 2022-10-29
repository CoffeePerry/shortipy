# coding=utf-8

"""shortipy.controllers.api module."""

from flask import Flask, Blueprint

from shortipy.controllers.api.auth import register_api as register_api_auth
from shortipy.controllers.api.url import register_api as register_api_url


def init_app() -> Flask | Blueprint:
    """Initializes the application API.

    :return: The Flask (or Blueprint) application instance.
    :rtype: Flask | Blueprint
    """
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    return register_api_url(register_api_auth(api_blueprint))
