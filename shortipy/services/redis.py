# coding=utf-8

"""shortipy.services.redis file."""

from flask import Flask
from flask_redis import FlaskRedis

redis_client = FlaskRedis()


def init_app(app: Flask) -> Flask:
    """Initializes the application Redis client.

    :param app: The Flask application instance.
    :type app: Flask
    :return: The Flask application instance.
    :rtype: Flask
    """
    redis_client.init_app(app, decode_responses=True)
    return app
