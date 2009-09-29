# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Performs event archivation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
import datetime,logging

T_LIMIT=100
class Task(noc.sa.periodic.Task):
    name="fm.archive"
    description=""
    
    def execute(self):
        from django.db import connection
        cursor=connection.cursor()
                
        from noc.fm.models import Event,EventArchivationRule
        now=datetime.datetime.now()
        # Process events
        cursor.execute("BEGIN")
        for rule in EventArchivationRule.objects.all():
            ts=now-datetime.timedelta(seconds=rule.ttl_seconds)
            if rule.action=="D":
                proc="delete_event(id)"
                status="C"
            elif rule.action=="C":
                proc="close_event(id,'Closed by archiver')"
                status="A"
            else:
                logging.error("fm.archive: Invalid rule action %s"%rule.action)
                continue
            while True:
                cursor.execute("SELECT COUNT(%s) FROM fm_event WHERE id IN (SELECT id FROM fm_event WHERE status=%%s AND timestamp<=%%s AND event_class_id=%%s LIMIT %d)"%(proc,T_LIMIT),
                    [status,ts,rule.event_class.id])
                c=cursor.fetchall()[0][0]
                cursor.execute("COMMIT")
                if c==0:
                    break
                logging.info("fm.archive: %d events of class '%s' are %s"%(c,rule.event_class.name,{"C":"closed","D":"dropped"}[rule.action]))
        cursor.execute("COMMIT")
        return True
