# coding=utf-8

"""shortipy.services.hash file."""

from hashlib import sha256

from flask import Flask
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


def init_app(app: Flask) -> Flask:
    """Initializes the application hash.

    :param app: The Flask application instance.
    :type app: Flask
    :return: The Flask application instance.
    :rtype: Flask
    """
    bcrypt.init_app(app)
    return app


def normalize_input(value: str | bytes) -> str:
    """Normalize input value.

    :param value: Input value.
    :type value: str | bytes
    :return: Normalized value.
    :rtype: str
    """
    if not value:
        raise Exception('Invalid value')
    if isinstance(value, str):
        value = bytes(value, 'utf-8')
    return sha256(value).hexdigest()
