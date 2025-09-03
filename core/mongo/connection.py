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
from pymongo.errors import AutoReconnect
from mongoengine.connection import (
    ConnectionFailure,
    connect as mongo_connect,
    _get_connection,
    _get_db,
)

# NOC modules
from noc.config import config


logger = logging.getLogger(__name__)
_connected = False


def connect():
    """
    Connect to the mongo database

    .. versionadded:: 19.3

    :return:
    """
    global _connected
    if _connected:
        return
    temporary_errors = (ConnectionFailure, AutoReconnect)
    retries = config.mongo.retries
    timeout = config.mongo.timeout

    ca = config.mongo_connection_args.copy()
    if ca.get("password"):
        ca["host"] = ca["host"].replace(":%s@" % ca["password"], ":********@")
        ca["password"] = "********"
    for i in range(retries):
        try:
            logger.info("Connecting to MongoDB %s", ca)
            connect_args = config.mongo_connection_args
            print("connect_args", connect_args, type(connect_args))
            mongo_connect(**connect_args)
            _connected = True
            break
        except temporary_errors as e:
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

    .. versionadded: 19.3

    :return: True if connect() has been called, False otherwise
    """
    global _connected
    return _connected


def get_connection():
    """

    :return:
    :rtype: pymongo.collection.Connection
    """
    return _get_connection()


def get_db():
    """

    :return:
    :rtype: pymongo.database.Database
    """
    return _get_db()
