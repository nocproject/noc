# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Performs event archivation
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.settings import config
from noc.fm.models import EventClass, ActiveEvent

class ArchiveJob(AutoIntervalJob):
    name = "fm.archive"
    interval = 300
    randomize = True

    def handler(self):
        w = config.getint("fm", "active_window")
        border = datetime.datetime.now() - datetime.timedelta(seconds=w)
        # Drop all events with event class action L
        to_drop = [c.id for c in EventClass.objects.filter(action="L")]
        dc = ActiveEvent.objects.filter(event_class__in=to_drop,
            timestamp__lte=border).count()
        if dc:
            ActiveEvent.objects.filter(event_class__in=to_drop,
                timestamp__lte=border).delete()
            self.info("%d active events cleaned (requested by event class)" % dc)
        # Drop all events not contributing to alarms
        dc = ActiveEvent.objects.filter(alarms__exists=False,
            timestamp__lte=border).count()
        if dc:
            ActiveEvent.objects.filter(alarms__exists=False,
                timestamp__lte=border).delete()
            self.info("%d active events cleaned (no related alarms)" % dc)
        # Archive other events
        n = 0
        for e in ActiveEvent.objects.filter(timestamp__lte=border):
            e.mark_as_archived("Archived by fm.archive task")
            n += 1
        if n:
            self.info("%d active events are moved into archive" % n)
        # Delete archived events without alarms
        return True
