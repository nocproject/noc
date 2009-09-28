# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.db import transaction,reset_queries
from noc.lib.daemon import Daemon
from noc.fm.models import Event,EventCorrelationRule
import logging,time,os,re,datetime

## Regular expression for embedded vars
rx_evar=re.compile(r"\${([^}]+?)}")
##
## Correlation rule
##
class Rule(object):
    def __init__(self,name,action,classes,vars,same_object,window):
        self.name=name
        self.action=action
        self.classes=classes # id
        self.vars=vars
        self.same_object=same_object
        self.window=window
        self.var_map=[]
        self.prepare_statement=None
        self.exec_statement=None
    ##
    ## Quote SQL string
    ##
    def q(self,s):
        return s.replace("\\","\\\\").replace("'","\\'")
    ##
    ## Generator returning a list of assotiated event classes
    ##
    def get_registered_event_classes(self):
        for c in self.classes:
            yield c
    ##
    ## Accepts SQL SELECT statements with embedded vars.
    ## Returns PREPARE statement and fills self.var_map
    ## Variables in SQL statement are encoded as ${NAME}
    ##
    def cook_prepare_statement(self,cursor,stmt,vars):
        order_map={}
        self.var_map=[]
        for i,v in enumerate(vars):
            order_map[v]=i+1
            self.var_map.append(vars[v])
        stmt=rx_evar.sub(lambda m:"$%d"%order_map[m.group(1)],stmt)
        stmt_name="stmt_%d"%id(self)
        stmt="PREPARE %s(%s) AS %s"%(stmt_name,",".join(["CHAR"]*len(order_map)),stmt)
        cursor.execute(stmt)
        self.prepare_statement=stmt
        self.exec_statement="EXECUTE %s(%s)"%(stmt_name,",".join(["%s"]*len(order_map)))
        logging.debug("SQL statement for rule '%s':\n%s"%(self.name,stmt))
    ##
    ## Executes "PREPARE" sql statement
    ##
    def prepare_sql_statement(self,cursor):
        pass
    ##
    ## Accepts a hash of event parameters
    ## and a hash of vars
    ## Returns a list of (event_id,action)
    ##
    def correlate(self,cursor,event,vars):
        try:
            cursor.execute(self.exec_statement,[f(event,vars) for f in self.var_map])
        except KeyError:
            # No required variable present in event
            return []
        return [(x[0],self.action) for x in cursor.fetchall()]
##
## Matches a nearest event of given classes with matching vars
##
class PairRule(Rule):
    def prepare_sql_statement(self,cursor):
        vars={
            "event_id"  : lambda e,v: e["event_id"],
            "timestamp" : lambda e,v: e["timestamp"]
        }
        # Create SQL select
        stmt="SELECT e.id FROM fm_event e"
        # Join tables
        for i,var in enumerate(self.vars):
            vars["var::%s"%var]=lambda e,v: v[var]
            stmt+=" JOIN fm_eventdata ed%d ON (e.id=ed%d.event_id)"%(i,i)
        stmt+=" WHERE "
        stmt+=" e.id!=${event_id}::int "
        stmt+=" AND e.timestamp<=${timestamp}::timestamp "
        # Restrict to window
        if self.window:
            stmt+=" AND e.timestamp>=(${timestamp}::timestamp-'%d seconds'::interval) "%int(self.window)
        # Restrint to event classes
        stmt+=" AND e.event_class_id IN (%s)"%(",".join(["%d"%c for c in self.classes ]))
        # Restrict search for same object if necessary
        if self.same_object:
            vars["managed_object_id"]=lambda e,v: e["managed_object_id"]
            stmt+=" AND e.managed_object_id=${managed_object_id}::int "
        for i,v in enumerate(self.vars):
            stmt+=" AND ed%d.key='%s' AND ed%d.value=${var::%s} "%(i,self.q(v),i,v)
        # Find nearest event
        stmt+=" ORDER BY e.timestamp DESC LIMIT 1"
        self.cook_prepare_statement(cursor,stmt,vars)

RULE_TYPE={
    "Pair" : PairRule,
}

##
## noc-correlator daemon
##
class Correlator(Daemon):
    daemon_name="noc-correlator"
    def __init__(self):
        from django.db import connection
        self.ec_to_rule={} # event_class_id -> list of applicable rules
        self.cursor=connection.cursor()
        Daemon.__init__(self)
        logging.info("Running Correlator")
    
    ##
    ## Load rules from database after loading config
    ##
    def load_config(self):
        super(Correlator,self).load_config()
        self.load_rules()
    ##
    ## Build rules
    ##
    def load_rules(self):
        logging.info("Loading rules")
        self.ec_to_rule={}
        n=0
        for r in EventCorrelationRule.objects.all():
            n+=1
            # Find rule class
            try:
                rc=RULE_TYPE[r.rule_type]
            except:
                logging.error("Unknown rule type '%s' in rule '%s'"%(r.rule_type,r.name))
                continue
            # Create rule object
            rule=rc(
                name=r.name,
                action=r.action,
                classes=[c.event_class.id for c in r.eventcorrelationmatchedclass_set.all()],
                vars=[c.var for c in r.eventcorrelationmatchedvar_set.all()],
                same_object=r.same_object,
                window=r.window)
            # Prepare SQL statement
            rule.prepare_sql_statement(self.cursor)
            # Associate rule object with classes
            for c in rule.get_registered_event_classes():
                if c not in self.ec_to_rule:
                    self.ec_to_rule[c]=[rule]
                else:
                    self.ec_to_rule[c].append(rule)
        logging.info("%d rules are loaded"%n)
        logging.debug("Rule map: %s"%str(self.ec_to_rule))
    ##
    ## Main daemon loop
    ##
    def run(self):
        INTERVAL=10
        last_id=0 # Max value of processes event.id
        transaction.enter_transaction_management()
        while True:
            n_closed=0
            n_checked=0
            t0=time.time()
            ws=datetime.datetime.now()-datetime.timedelta(seconds=self.config.getint("correlator","window")) # Start of the window
            for e in Event.objects.filter(status="A",timestamp__gte=ws,id__gte=last_id).order_by("timestamp"):
                n_checked+=1
                last_id=max(last_id,e.id)
                event_class_id=e.event_class.id
                if event_class_id not in self.ec_to_rule:
                    continue # No matching rules
                # Prepare hashes
                ts=e.timestamp
                event={
                    "event_id"          : str(e.id),
                    "timestamp"         : "%04d-%02d-%02d %02d:%02d:%02d"%(ts.year,ts.month,ts.day,ts.hour,ts.minute,ts.second),
                    "managed_object_id" : str(e.managed_object.id),
                }
                vars=dict([(d.key,d.value) for d in e.eventdata_set.all()])
                # Try to correlate events
                for r in self.ec_to_rule[event_class_id]:
                    for e_id,action in r.correlate(self.cursor,event,vars):
                        if action=="C":
                            # Close event
                            ce=Event.objects.get(id=e_id)
                            if ce.status=="A":
                                ce.close_event("Event closed by event %d (Correlation rule: %s)"%(e.id,r.name))
                                logging.debug("Event %d closed by event %d (Correlation rule: %s)"%(e_id,e.id,r.name))
                                n_closed+=1
                        transaction.commit() # Execute each correlation query inside own transaction
                        reset_queries()
            # Dump performance data
            if n_closed:
                dt=time.time()-t0
                logging.info("%d events were closed in %d seconds (%d events checked)"%(n_closed,dt,n_checked))
            else:
                time.sleep(INTERVAL)
        transaction.leave_transaction_management()
