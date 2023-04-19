# coding=utf-8

"""tests.test_shortipy file."""

from os import linesep, path, mkdir, rmdir, remove, rename
from secrets import token_bytes

from flask import Flask
from flask.testing import FlaskCliRunner
from pytest import raises

from shortipy import CONFIG_FILENAME, VERSION, create_app
from shortipy.services.config import Config


def test_create_app(application: Flask):
    """Test factory and config.

    :param application: Flask application.
    :type application: Flask
    """
    todo_remove_dir = False
    if not path.isdir(application.instance_path):
        mkdir(application.instance_path)
        todo_remove_dir = True
    config_filename = path.join(application.instance_path, CONFIG_FILENAME)
    todo_remove_file = False
    if not path.isfile(config_filename):
        with open(config_filename, 'w', encoding='utf8') as file:
            file.write('SECRET_KEY=\'test\'')
        todo_remove_file = True
    try:
        assert not create_app().testing
        assert create_app({'TESTING': True, 'SECRET_KEY': token_bytes(32)}).testing
    finally:
        try:
            if todo_remove_file and path.isfile(config_filename):
                remove(config_filename)
        finally:
            if todo_remove_dir and path.isdir(application.instance_path):
                rmdir(application.instance_path)


def test_config(application: Flask):  # pylint: disable=too-many-branches
    """Test config.

    :param application: Flask application.
    :type application: Flask
    """
    with raises(Exception, match='Invalid options'):
        create_app('TESTING')

    if path.isdir(application.instance_path):
        rename(application.instance_path, f'{application.instance_path}_bak')
    try:
        with raises(Exception, match=r'Directory not found, so just created: .*.' + linesep +
                                     f'Put file "{CONFIG_FILENAME}" inside, please.'):
            create_app()

        if not path.isdir(application.instance_path):
            mkdir(application.instance_path)
        config_filename = path.join(application.instance_path, CONFIG_FILENAME)
        if path.isfile(config_filename):
            rename(config_filename, f'{config_filename}.bak')
        try:
            with raises(Exception, match=r'Configuration file not found(.*)'):
                create_app()
            with application.app_context():
                with open(config_filename, 'wb'):
                    pass
            try:
                with raises(Exception, match=r'Set variable SECRET_KEY with random string in file: .*'):
                    create_app()
            finally:
                if path.isfile(config_filename):
                    remove(config_filename)
        finally:
            if path.isfile(f'{config_filename}.bak'):
                rename(f'{config_filename}.bak', config_filename)
    finally:
        try:
            if path.isdir(application.instance_path):
                rmdir(application.instance_path)
        finally:
            if path.isdir(f'{application.instance_path}_bak'):
                rename(f'{application.instance_path}_bak', application.instance_path)


def test_config_class():
    """Test Config class."""
    config = Config()
    properties = config.get_dict()
    assert config.DEBUG == properties['DEBUG']
    assert config.SESSION_COOKIE_SECURE == properties['SESSION_COOKIE_SECURE']
    assert config.SESSION_COOKIE_HTTPONLY == properties['SESSION_COOKIE_HTTPONLY']
    assert config.SECRET_KEY == properties['SECRET_KEY']
    assert config.REDIS_URL == properties['REDIS_URL']


def test_version(runner: FlaskCliRunner):
    """Test CLI version.

    :param runner: Flask CLI Runner.
    :type runner: FlaskCliRunner
    """
    result = runner.invoke(args=['version'])
    assert result.output == f'Shortipy v{VERSION}\n'
