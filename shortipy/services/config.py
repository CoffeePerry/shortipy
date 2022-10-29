# coding=utf-8

# pylint: disable=invalid-name

"""shortipy.services.config file."""


class Config:  # pylint: disable=too-few-public-methods
    """Class to manage basic configurations."""

    def __init__(self):
        """Config constructor."""
        self.DEBUG = False

        # Flask
        self.SECRET_KEY = None
        self.SESSION_COOKIE_SECURE = True
        self.SESSION_COOKIE_HTTPONLY = True

        # Flask JWT Extended
        self.JWT_SECRET_KEY = None

        # Flask Redis
        self.REDIS_URL = 'redis://127.0.0.1:6379/0'

        # Flask Marshmallow
        self.JSON_SORT_KEYS = False

    def get_dict(self) -> dict:
        """Get Config dict.

        :return: Config dict.
        :rtype: dict
        """
        result = {}
        for key in dir(self):
            if key.isupper():
                result[key] = getattr(self, key)
        return result
