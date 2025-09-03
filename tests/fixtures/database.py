# ----------------------------------------------------------------------
# Database fixture and utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.config import config
from noc.core.mongo.connection import connect as mongo_connect


@pytest.fixture(scope="session")
def database(request):
    """
    Create and destroy test databases
    :param request:
    :return:
    """
    # Create databases
    _create_pg_db()
    # _create_mongo_db()
    _create_clickhouse_db()
    # Return control to the test
    yield
    # Cleanup databases
    _drop_pg_db()
    # _drop_mongo_db()
    _drop_clickhouse_db()


def _create_pg_db():
    """
    Create postgres test database
    :return:
    """
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    db = config.pg_connection_args.copy()
    db["database"] = "postgres"
    connect = psycopg2.connect(**db)
    connect.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connect.cursor()
    cursor.execute("CREATE DATABASE %s ENCODING 'UTF-8'" % config.pg.db)
    cursor.close()
    connect.close()


def _create_mongo_db():
    """
    Create mongodb test database
    :return:
    """
    # MongoDB creates database automatically on connect
    mongo_connect()


def _create_clickhouse_db():
    """
    Create clickhouse test database
    :return:
    """


def _drop_pg_db():
    """
    Drop postgresql test database
    :return:
    """
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    tpl = config.pg_connection_args.copy()
    tpl["database"] = "postgres"
    connect = psycopg2.connect(**tpl)
    connect.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connect.cursor()
    # Forcefully disconnect remaining connections
    cursor.execute(
        """
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = %s
    """,
        [config.pg.db],
    )
    # Drop
    cursor.execute("DROP DATABASE IF EXISTS %s" % config.pg.db)
    cursor.close()
    connect.close()


def _drop_mongo_db():
    """
    Drop mongodb database
    :return:
    """
    import mongoengine

    client = mongoengine.connect(**config.mongo_connection_args)
    client.drop_database(config.mongo.db)
    client.close()


def _drop_clickhouse_db():
    """
    Drop clickhouse database
    :return:
    """
