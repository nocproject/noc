# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Performs event archivation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import datetime
import logging
## NOC modules
import noc.lib.periodic
from noc.settings import config

class Task(noc.lib.periodic.Task):
    name = "fm.archive"
    description = ""
    
    def execute(self):
        from noc.fm.models import EventClass, ActiveEvent
        
        w = config.getint("fm", "active_window")
        border = datetime.datetime.now() - datetime.timedelta(seconds=w)
        # Drop all events with event class action L
        to_drop = [c.id for c in EventClass.objects.filter(action="L")]
        dc = ActiveEvent.objects.filter(event_class__in=to_drop,
                                        timestamp__lte=border).count()
        if dc:
            ActiveEvent.objects.filter(event_class__in=to_drop,
                                        timestamp__lte=border).delete()
            self.info("%d active events cleaned" % dc)
        # Archive other events
        n = 0
        for e in ActiveEvent.objects.filter(timestamp__lte=border):
            e.mark_as_archived("Archived by fm.archive task")
            n += 1
        if n:
            self.info("%d active events are moved into archive" % n)
        return True
