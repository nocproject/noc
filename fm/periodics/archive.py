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
import datetime

class Task(noc.sa.periodic.Task):
    name="fm.archive"
    description=""
    
    def execute(self):
        from django.db import connection
        cursor=connection.cursor()
                
        from noc.fm.models import Event,EventArchivationRule
        
        cursor.execute("BEGIN")
        for rule in EventArchivationRule.objects.all():
            ts=datetime.datetime.now()-datetime.timedelta(seconds=rule.ttl*{"s":1,"m":60,"h":3600,"d":86400}[rule.ttl_measure])
            while True:
                cursor.execute("SELECT COUNT(delete_event(id)) FROM fm_event WHERE id IN (SELECT id FROM fm_event WHERE status=%s AND timestamp<=%s AND event_class_id=%s LIMIT 100)",
                    ["C",ts,rule.event_class.id])
                c=cursor.fetchall()[0][0]
                cursor.execute("COMMIT")
                if c==0:
                    break
        return True

