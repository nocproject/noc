# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PostgreSQL probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes import *

class PostgreSQLProbe(Probe):
    name="postgresql"
    
    # List of (name,type,sp_name)
    DB_SP_COUNTERS=[
        ("num_backends",   "pg_stat_get_db_numbackends"),
        ("xact_commit",    "pg_stat_get_db_xact_commit"),
        ("xact_rollback",  "pg_stat_get_db_xact_rollback"),
        ("blocks_fetched", "pg_stat_get_db_blocks_fetched"),
        ("blocks_hit",     "pg_stat_get_db_blocks_hit"),
    ]
    
    parameters={
        "num_backends"   : {"type": "gauge"},
        "xact_commit"    : {"type": "counter"},
        "xact_rollback"  : {"type": "counter"},
        "blocks_fetched" : {"type": "counter"},
        "blocks_hit"     : {"type": "counter"},
    }
    
    def __init__(self,daemon,probe_name,config):
        super(PostgreSQLProbe,self).__init__(daemon,probe_name,config)
        self.dsn=self.get("dsn")
        self.connect=None
        self.cursor=None
        self.db_query="SELECT datname,"+",".join([x[1]+"(datid)" for x in self.DB_SP_COUNTERS])\
            +" FROM pg_stat_database WHERE datname IN (%s)"%",".join(["'%s'"%s for s in self.services])
        self.db_param=[x[0] for x in self.DB_SP_COUNTERS[1:]]
    
    def get_cursor(self):
        import psycopg2
        if self.connect is None:
            self.connect=psycopg2.connect(self.dsn)
            self.cursor=None
        if self.cursor is None:
            self.cursor=self.connect.cursor()
        return self.cursor
    
    def sql(self,query):
        c=self.get_cursor()
        c.execute(query)
        return c.fetchall()
    
    def on_start(self):
        for row in self.sql(self.db_query):
            service=row[0]
            for param,value in zip(self.db_param,row[1:]):
                self.set_data(service,param,value)
        self.exit()
    
    def on_stop(self):
        pass
