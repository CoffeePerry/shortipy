# coding=utf-8

"""shortipy.services.exceptions file."""

from werkzeug.exceptions import HTTPException


class MethodVersionNotFound(HTTPException):
    """*400* `Method Version Not Found` (Bad Request)
    Raise if the browser request method through an invalid method version ('Accept-Version').
    (Raise if the browser sends something to the application or server cannot handle).
    """

    code = 400
    description = (
        "Bad Request - Method Version Not Found: The browser (or proxy) request an invalid method's version."
    )
