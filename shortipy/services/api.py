# coding=utf-8

"""shortipy.controllers.api file."""

from flask import Flask, Blueprint
from flask_restful import Api

from shortipy.controllers.api import init_api

api = Api()


def init_app(app: Flask | Blueprint) -> Flask | Blueprint:
    """Initializes the application API.

    :param app: The Flask (or Blueprint) application instance.
    :type app: Flask | Blueprint
    :return: The Flask (or Blueprint) application instance.
    :rtype: Flask | Blueprint
    """
    init_api(api)
    if isinstance(app, Flask):
        api.init_app(app)
    return app
