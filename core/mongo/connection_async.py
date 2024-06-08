# ----------------------------------------------------------------------
# Mongo connection setup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import time
import sys

# Third-party modules
from motor.motor_asyncio import AsyncIOMotorClient

# NOC modules
from noc.config import config


DEFAULT_CONNECTION_NAME = "default"

logger = logging.getLogger(__name__)
_async_connections = {}
_dbs = {}


def connect_async():
    """
    Connect to the mongo database

    .. versionadded:: 21.1

    :return:
    """
    global _async_connections
    if _async_connections:
        return
    # temporary_errors = (ConnectionFailure, AutoReconnect)
    retries = config.mongo.retries
    timeout = config.mongo.timeout

    ca = config.mongo_connection_args.copy()
    if ca.get("password"):
        ca["host"] = ca["host"].replace(":%s@" % ca["password"], ":********@")
        ca["password"] = "********"
    for i in range(retries):
        try:
            logger.info("Connecting to MongoDB %s", ca)
            connection_args = config.mongo_connection_args.copy()
            connection_args["authSource"] = connection_args.pop("authentication_source")
            connection_args.pop("db")
            _async_connections[DEFAULT_CONNECTION_NAME] = AsyncIOMotorClient(**connection_args)
            break
        except Exception as e:
            logger.error("Cannot connect to mongodb: %s", e)
            if i < retries - 1:
                logger.error("Waiting %d seconds", timeout)
                time.sleep(timeout)
            else:
                logger.error("Cannot connect %d times. Exiting", retries)
                sys.exit(1)


def is_connected():
    """
    Check if mongo database connection is active

    .. versionadded: 21.1

    :return: True if connect() has been called, False otherwise
    """
    global _async_connections
    return bool(_async_connections)


def get_connection():
    """

    :return:
    :rtype: pymongo.collection.Connection
    """
    global _async_connections
    if DEFAULT_CONNECTION_NAME in _async_connections:
        return _async_connections[DEFAULT_CONNECTION_NAME]


def get_db():
    """

    :return:
    :rtype: pymongo.database.Database
    """
    global _dbs
    if DEFAULT_CONNECTION_NAME not in _dbs:
        conn = get_connection()
        _dbs[DEFAULT_CONNECTION_NAME] = conn.get_default_database()
    return _dbs[DEFAULT_CONNECTION_NAME]
