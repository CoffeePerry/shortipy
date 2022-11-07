# coding=utf-8

"""shortipy.services.auth file."""

from typing import Final

from click import option, STRING
from flask import Flask
from flask.cli import AppGroup
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.exceptions import NotFound, Unauthorized

from shortipy.services.redis import redis_client
from shortipy.services.hash import bcrypt, normalize_input

USER_KEYS_DOMAIN: Final = 'user'

jwt = JWTManager()
cli = AppGroup('users', help='Manage users.')


def init_app(app: Flask) -> Flask:
    """Initializes the application auth.

    :param app: The Flask application instance.
    :type app: Flask
    :return: The Flask application instance.
    :rtype: Flask
    """
    jwt.init_app(app)
    app.cli.add_command(cli)
    return app


def insert_user(username: str, password: str | bytes):
    """Insert new user.

    :param username: User's username.
    :type username: str
    :param password: User's password.
    :type password: str | bytes
    """
    if redis_client.hget(f'{USER_KEYS_DOMAIN}:{username}', 'password') is not None:
        raise Exception(f'User "{username}" already exists')

    password_hash = bcrypt.generate_password_hash(normalize_input(password))

    redis_client.hset(f'{USER_KEYS_DOMAIN}:{username}', 'password', password_hash)


def delete_user(username: str):
    """Delete user.

    :param username: User's username.
    :type username: str
    """
    if not redis_client.hgetall(f'{USER_KEYS_DOMAIN}:{username}'):
        raise NotFound(f'User "{username}" not found')

    redis_client.delete(f'{USER_KEYS_DOMAIN}:{username}')


def login(username: str, password: str | bytes) -> str:
    """Do login.

    :param username: User's username.
    :type username: str
    :param password: User's password.
    :type password: str | bytes
    :return: Access token.
    :rtype: str
    """
    if not bcrypt.check_password_hash(redis_client.hget(f'{USER_KEYS_DOMAIN}:{username}', 'password'), normalize_input(password)):
        raise Unauthorized('Bad username or password')

    access_token = create_access_token(identity=username)
    return access_token


# region CLI functions
@cli.command('new', help='Insert new user.')
@option('-u', '--username', type=STRING, prompt='Enter the user\'s username', help='Specify the user\'s username.')
@option('-p', '--password', type=STRING, prompt='Enter the user\'s password', help='Specify the user\'s password.')
def new_user(username: str, password: str):
    """Insert new user.

    :param username: User's username.
    :type username: str
    :param password: User's password.
    :type password: str
    """
    print(f'Insert user: {username}...')
    insert_user(username, password)
    print('Done.')


@cli.command('del', help='Delete user by username.')
@option('-u', '--username', type=STRING, prompt='Enter the user\'s username', help='Specify the user\'s username.')
def del_url(username: str):
    """Delete user by username.

    :param username: User's username.
    :type username: str
    """
    print(f'Deleting user: {username}...')
    delete_user(username)
    print('Done.')
# endregion
