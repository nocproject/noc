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

    parameters={
        "num_backends"    : {"type": "gauge"},
        "xact_commit"     : {"type": "counter"},
        "xact_rollback"   : {"type": "counter"},
        "blocks_fetched"  : {"type": "counter"},
        "blocks_hit"      : {"type": "counter"},
        "records_returned": {"type": "counter"},
        "records_fetched" : {"type": "counter"},
        "records_inserted": {"type": "counter"},
        "records_updated" : {"type": "counter"},
        "records_deleted" : {"type": "counter"},
    }

    PG_STAT_DATABASE_COUNTERS={
        "numbackends"   : "num_backends",
        "xact_commit"   : "xact_commit",
        "xact_rollback" : "xact_rollback",
        "blks_read"     : "blocks_fetched",
        "blks_hit"      : "blocks_hit",
        "tup_returned"  : "records_returned",
        "tup_fetched"   : "records_fetched",
        "tup_inserted"  : "records_inserted",
        "tup_updated"   : "records_updated",
        "tup_deleted"   : "records_deleted",
    }
        
    def __init__(self,daemon,probe_name,config):
        super(PostgreSQLProbe,self).__init__(daemon,probe_name,config)
        self.dsn=self.get("dsn")
        self.connect=None
        self.cursor=None
        self.pg_stat_names=[]
        self.pg_stat_params=[]
        for n,p in self.PG_STAT_DATABASE_COUNTERS.items():
            self.pg_stat_names+=[n]
            self.pg_stat_params+=[p]
        self.db_query="SELECT datname,"+",".join(self.pg_stat_names)\
            +" FROM pg_stat_database WHERE datname IN (%s)"%",".join(["'%s'"%s for s in self.services])
    
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
            for param,value in zip(self.pg_stat_params,row[1:]):
                self.set_data(service,param,value)
        self.get_cursor().execute("COMMIT")
        self.exit()
    
    def on_stop(self):
        pass
