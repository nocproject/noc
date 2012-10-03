# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PowerDNS/MySQL sync backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import MySQLdb
## NOC modules
from _dbapi import PowerDNSDBAPIChannel


class PowerDNSMySQLChannel(PowerDNSDBAPIChannel):
    """
    Config example:

    [dns/zone/ch1]
    type = powerdns/mysql
    enabled = true
    database = db=dns user=user host=127.0.0.1 passwd=pass
    """
    def get_database(self, db_string):
        dbc = dict(x.split("=", 1) for x in db_string.split())
        return MySQLdb.connect(**dbc)
