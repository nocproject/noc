# ----------------------------------------------------------------------
# Autocommit pg database wrapper
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson
import psycopg2
from django.db.backends.postgresql.base import DatabaseWrapper as PGDatabaseWrapper
from django.db.backends.postgresql.operations import DatabaseOperations as PGDatabaseOperations
from django.db.backends.postgresql.psycopg_any import Jsonb

# NOC modules
from .monitor import SpanCursor


class DatabaseOperations(PGDatabaseOperations):
    def adapt_json_value(self, value, encoder):
        def dumps(obj):
            return orjson.dumps(obj).decode("utf-8")

        return Jsonb(value, dumps=dumps)


class DatabaseWrapper(PGDatabaseWrapper):
    ops_class = DatabaseOperations

    def _savepoint_allowed(self):
        return False

    def get_new_connection(self, conn_params):
        """
        Return raw psycopg connection. Do not mess with django setup phase
        :param conn_params:
        :return:
        """
        conn_params["cursor_factory"] = SpanCursor
        connection = psycopg2.connect(**conn_params)
        # Register dummy loads() to avoid a round trip from psycopg2's decode
        # to json.dumps() to json.loads(), when using a custom decoder in
        # JSONField.
        psycopg2.extras.register_default_jsonb(conn_or_curs=connection, loads=lambda x: x)
        return connection

    def init_connection_state(self):
        """
        :return:
        """
        self.connection.autocommit = True
        self.connection.set_client_encoding("UTF8")

    def _set_isolation_level(self, level):
        pass

    def _set_autocommit(self, state):
        pass
