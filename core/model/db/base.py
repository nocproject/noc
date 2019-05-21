# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Autocommit pg database wrapper
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.backends.postgresql_psycopg2.base import \
    DatabaseWrapper as PGDatabaseWrapper


class DatabaseWrapper(PGDatabaseWrapper):
    def _savepoint_allowed(self):
        return False
