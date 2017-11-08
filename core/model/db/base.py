# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Autocommit pg database wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from django.db.backends.postgresql_psycopg2.base import \
    DatabaseWrapper as PGDatabaseWrapper


class DatabaseWrapper(PGDatabaseWrapper):
    def _enter_transaction_management(self, managed):
        """
        Switch the isolation level when needing transaction support, so that
        the same transaction is visible across all the queries.
        """
        pass

    def _leave_transaction_management(self, managed):
        """
        If the normal operating mode is "autocommit", switch back to that when
        leaving transaction management.
        """
        pass

    def _commit(self):
        pass
