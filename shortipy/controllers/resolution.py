# coding=utf-8

"""shortipy.controllers.resolution file."""

from flask import Blueprint, Response, redirect, abort
from markupsafe import escape

from shortipy.services.redis import redis_client

resolution_blueprint = Blueprint('resolution', __name__)


@resolution_blueprint.route('/<key>')
def resolve(key: str) -> Response:
    """Resolve the key in the correspondent url and redirect.

    :param key: Key to resolve.
    :type key: str
    :return: Flask response.
    :rtype: Response
    """
    value = redis_client.get(f'url:{escape(key)}')
    if value is None:
        abort(404)
    return redirect(value)
