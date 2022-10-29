# coding=utf-8

"""shortipy.controllers.api.auth file."""

from flask import Flask, Blueprint, request
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import use_args
from marshmallow.validate import Length

from shortipy.services.exceptions import MethodVersionNotFound
from shortipy.services.serialization import marshmallow
from shortipy.services.auth import login


class AuthSchema(marshmallow.Schema):
    """Class to define auth schema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class Meta."""

        ordered = True
        fields = ('username', 'access_token')


class AuthListAPI(MethodView):
    """Auth list API."""

    init_every_request = False

    def __init__(self):
        """AuthListAPI constructor."""
        self.auth_schema = AuthSchema()

    @use_args({
        'username': fields.Str(required=True, validate=Length(min=1)),
        'password': fields.Str(required=True, validate=Length(min=1))
    }, location='json')
    def post(self, args: dict):
        """Post login.

        :param args: Arguments.
        :type args: dict
        :return: Inserted url.
        :rtype: dict[str, str]
        """
        if request.headers.get('Accept-Version', '1.0') == '1.0':
            return {'auth': self.auth_schema.dump({
                'username': args['username'],
                'access_token': login(args['username'], args['password'])
            })}
        raise MethodVersionNotFound()


def register_api(app: Flask | Blueprint) -> Flask | Blueprint:
    """Register API controller.

    :param app: The Flask (or Blueprint) application instance.
    :type app: Flask | Blueprint
    :return: The Flask (or Blueprint) application instance.
    :rtype: Flask | Blueprint
    """
    app.add_url_rule('/auth/', view_func=AuthListAPI.as_view('auth'))
    return app
