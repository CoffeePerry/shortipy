# coding=utf-8

"""shortipy.services.serialization file."""

from flask import Flask
from flask_marshmallow import Marshmallow

marshmallow = Marshmallow()


def init_app(app: Flask) -> Flask:
    """Initializes the application serialization.

    :param app: The Flask application instance.
    :type app: Flask
    :return: The Flask application instance.
    :rtype: Flask
    """
    marshmallow.init_app(app)
    return app
