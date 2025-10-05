# ----------------------------------------------------------------------
# VCenter Connection Setup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from pyVim.connect import Disconnect, SmartConnect


DEFAULT_CONNECTION_NAME = "default"

logger = logging.getLogger(__name__)
_vim_connection_settings = {}
_vim_connections = {}


class ConnectionFailure(Exception):
    """Error raised when the database connection can't be established or
    when a connection with a requested alias can't be retrieved.
    """


def disconnect(alias=DEFAULT_CONNECTION_NAME):
    """Close the connection with a given alias."""
    global _vim_connections, _vim_connection_settings

    connection = _vim_connections.pop(alias, None)
    if connection:
        logger.info("[%s] Close VIM connection", alias)
        Disconnect(connection)

    if alias in _vim_connection_settings:
        del _vim_connection_settings[alias]


def disconnect_all():
    """Close all registered database."""
    global _vim_connections

    for alias in list(_vim_connections.keys()):
        disconnect(alias)


def register_connection(
    alias,
    host=None,
    port=None,
    username=None,
    password=None,
):
    """Register connection settings"""
    global _vim_connection_settings

    conn_settings = {
        "host": host,
        "user": username,
        "pwd": password,
        "disableSslCertValidation": True,
    }
    _vim_connection_settings[alias] = conn_settings


def _create_connection(alias, **connection_settings):
    """
    Create the new connection for this alias. Raise
    ConnectionFailure if it can't be established.
    """
    try:
        return SmartConnect(**connection_settings)
    except Exception as e:
        raise ConnectionFailure(f"Cannot connect to VCenter {alias} :\n{e}")


def connect(host=None, alias=DEFAULT_CONNECTION_NAME, **kwargs):
    """Connect to"""
    global _vim_connections, _vim_connection_settings

    if alias in _vim_connections:
        prev_conn_setting = _vim_connection_settings[alias]
        # Token ?
        new_conn_settings = {
            "host": host,
            "user": kwargs.get("username"),
            "pwd": kwargs.get("password"),
            "disableSslCertValidation": True,
        }

        if new_conn_settings != prev_conn_setting:
            err_msg = (
                "A different connection with alias `{}` was already "
                "registered. Use disconnect() first"
            ).format(alias)
            raise ConnectionFailure(err_msg)
    else:
        register_connection(alias, host, **kwargs)

    return get_connection(alias)


def get_connection(alias=DEFAULT_CONNECTION_NAME, reconnect=False):
    """Return a connection with a given alias."""
    global _vim_connections, _vim_connection_settings

    # If the requested alias already exists in the _connections list, return
    # it immediately.
    if alias in _vim_connections:
        return _vim_connections[alias]

    # Validate that the requested alias exists in the _connection_settings.
    # Raise ConnectionFailure if it doesn't.
    if alias not in _vim_connection_settings:
        if alias == DEFAULT_CONNECTION_NAME:
            msg = "You have not defined a default connection"
        else:
            msg = 'Connection with alias "%s" has not been defined' % alias
        raise ConnectionFailure(msg)

    conn_settings = _vim_connection_settings[alias].copy()

    if alias in _vim_connections:
        connection = alias
    else:
        connection = _create_connection(alias=alias, **conn_settings)

    _vim_connections[alias] = connection
    return _vim_connections[alias]
