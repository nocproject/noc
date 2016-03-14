# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PostgreSQL connection pool
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import psycopg2.pool
## NOC modules
from api.sae import SAEAPI


class PreparedConnectionPool(psycopg2.pool.ThreadedConnectionPool):
    def _connect(self, key=None):
        connect = super(PreparedConnectionPool, self)._connect(key)
        connect.autocommit = True
        cursor = connect.cursor()
        cursor.execute(SAEAPI.PREPARE_SQL)
        return connect
