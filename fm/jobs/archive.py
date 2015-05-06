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
from noc.fm.models import EventClass, ActiveEvent, ArchivedEvent

class ArchiveJob(AutoIntervalJob):
    name = "fm.archive"
    interval = 300
    randomize = True

    def handler(self):
        w = config.getint("fm", "active_window")
        woa = config.getint("fm", "keep_events_wo_alarm")
        wa = config.getint("fm", "keep_events_with_alarm")
        border = datetime.datetime.now() - datetime.timedelta(seconds=w)
        # Drop all events with event class action L
        to_drop = [c.id for c in EventClass.objects.filter(action="L")]
        dc = ActiveEvent.objects.filter(event_class__in=to_drop,
            timestamp__lte=border).count()
        if dc:
            ActiveEvent.objects.filter(event_class__in=to_drop,
                timestamp__lte=border).delete()
            self.info("%d active events cleaned (requested by event class)" % dc)
        ## Events without alarms
        if woa == 0:
            # Drop all events not contributing to alarms
            dc = ActiveEvent.objects.filter(alarms__exists=False,
                timestamp__lte=border).count()
            if dc:
                ActiveEvent.objects.filter(alarms__exists=False,
                    timestamp__lte=border).delete()
                self.info("%d active events cleaned (no related alarms)" % dc)
        ## Events with alarms
        if wa == 0:
            # Drop all events contributing to alarms
            dc = ActiveEvent.objects.filter(alarms__exists=True,
                timestamp__lte=border).count()
            if dc:
                ActiveEvent.objects.filter(alarms__exists=True,
                    timestamp__lte=border).delete()
                self.info("%d active events cleaned (with related alarms)" % dc)
        # Archive left events
        n = 0
        for e in ActiveEvent.objects.filter(timestamp__lte=border):
            e.mark_as_archived("Archived by fm.archive job")
            n += 1
        if n:
            self.info("%d active events are moved into archive" % n)
        # Cleanup archive
        if woa > 0:
            border = datetime.datetime.now() - datetime.timedelta(days=woa)
            dc = ArchivedEvent.objects.filter(
                alarms__exists=False, timestamp__lte=border).count()
            if dc:
                ArchivedEvent.objects.filter(
                    alarms__exists=False, timestamp__lte=border).delete()
                self.info("%d archived events cleaned (no related alarms)")
        if wa > 0:
            border = datetime.datetime.now() - datetime.timedelta(days=wa)
            dc = ArchivedEvent.objects.filter(
                alarms__exists=True, timestamp__lte=border).count()
            if dc:
                ArchivedEvent.objects.filter(
                    alarms__exists=True, timestamp__lte=border).delete()
                self.info("%d archived events cleaned (with related alarms)")
        return True
