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
from pymongo.mongo_client import MongoClient
from pymongo.errors import AutoReconnect
from pymongo.database import Database
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


def connect() -> None:
    """
    Establish connection to the MongoDB database.

    The function initializes the MongoDB connection using configured
    connection parameters. If the connection is already established,
    no action is performed.

    Temporary connection errors are retried according to the configured
    retry count and timeout. The process exits if the connection cannot
    be established after all retries.
    """
    global _connected
    if _connected:
        return
    temporary_errors = (ConnectionFailure, AutoReconnect)
    retries = config.mongo.retries
    timeout = config.mongo.timeout

    ca = config.mongo_connection_args.copy()
    if ca.get("password"):
        ca["host"] = ca["host"].replace(f":{ca['password']}@", ":********@")
        ca["password"] = "********"
    for i in range(retries):
        try:
            logger.info("Connecting to MongoDB %s", ca)
            connect_args = config.mongo_connection_args
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


def is_connected() -> bool:
    """
    Check whether the MongoDB connection has been established.

    Returns:
        True: if connect() has been called
        False:  otherwise
    """
    global _connected
    return _connected


def get_connection() -> MongoClient:
    """
    Get the current MongoDB client instance.

    Returns:
        MongoDB client instance.
    """
    return _get_connection()


def get_db() -> Database:
    """
    Get the current MongoDB database instance.

    Returns:
        MongoDB database instance.
    """
    return _get_db()
