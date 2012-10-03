# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PowerDNS/PostgreSQL sync backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import psycopg2
## NOC modules
from _dbapi import PowerDNSDBAPIChannel


class PowerDNSPgSQLChannel(PowerDNSDBAPIChannel):
    """
    Config example:

    [dns/zone/ch1]
    type = powerdns/pgsql
    enabled = true
    database = dbname=dns user=user
    """
    def get_database(self, db_string):
        return psycopg2.connect(db_string)
