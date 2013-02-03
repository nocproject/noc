# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database Context
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
from django.db import connection
## Third-party modules
import psycopg2
## NOC modules
from noc.lib import nosql


class DatabaseContext(object):
    """
    Database context manager
    """
    def __init__(self, parent, reuse=False, interactive=False, verbosity=1):
        self.parent = parent
        self.reuse = reuse
        self.autoclobber = not interactive
        self.verbosity = verbosity
        self.dbname = connection.settings_dict["NAME"]
        self.test_dbname = connection.creation._get_test_db_name()
        connection.creation.prepare_for_test_db_ddl = self._fixup

    def info(self, message):
        logging.info(message)

    def debug(self, message):
        logging.debug(message)

    def has_pg_db(self):
        """
        Check PosgreSQL test database already exists
        """
        dsn = ["dbname=%s" % self.test_dbname]
        if connection.settings_dict["USER"]:
            dsn += ["user=%s" % connection.settings_dict["USER"]]
        if connection.settings_dict["PASSWORD"]:
            dsn += ["password=%s" % connection.settings_dict["PASSWORD"]]
        dsn = " ".join(dsn)
        try:
            self.debug("Checking PostgreSQL database %s exists" % self.test_dbname)
            psycopg2.connect(dsn)
            self.debug("PostgreSQL database %s is already exists" % self.test_dbname)
            return True
        except psycopg2.OperationalError:
            return False

    def _fixup(self):
        # psycopg  2.4.2/Django 1.3.1 autocommit fixup
        # See https://code.djangoproject.com/ticket/16250 for details
        connection.connection.rollback()
        connection.connection.set_isolation_level(0)

    def __enter__(self):
        if self.reuse:
            return
        self.info("Creating PostgreSQL test database")
        # Create PostgreSQL database
        connection.creation.create_test_db(self.verbosity,
                                           autoclobber=self.autoclobber)
        self.info("Creating MongoDB test database")
        # MongoDB
        nosql.create_test_db(self.verbosity, autoclobber=self.autoclobber)

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.reuse:
            # PostgreSQL
            self.info("Destroying PostgreSQL test database")
            connection.creation.destroy_test_db(self.dbname, self.verbosity)
            # MongoDB
            self.info("Destroying MongoDB test database")
            nosql.destroy_test_db(self.verbosity)
