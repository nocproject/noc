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
        from noc.fm.models import Event,EventArchivationRule
        
        for rule in EventArchivationRule.objects.all():
            ts=datetime.datetime.now()-datetime.timedelta(seconds=rule.ttl*{"s":1,"m":60,"h":3600,"d":86400}[rule.ttl_measure])
            Event.objects.filter(status="C",timestamp__lte=ts,event_class=rule.event_class).delete()
        return True

