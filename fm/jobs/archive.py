# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Performs event archivation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# NOC modules
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.config import config
from noc.fm.models.eventclass import EventClass
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent

=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class ArchiveJob(AutoIntervalJob):
    name = "fm.archive"
    interval = 300
    randomize = True
<<<<<<< HEAD
    threaded = True
    transaction = True

    def handler(self):
        w = config.fm.active_window
        woa = config.fm.keep_events_wo_alarm
        wa = config.fm.keep_events_with_alarm
=======

    def handler(self):
        w = config.getint("fm", "active_window")
        woa = config.getint("fm", "keep_events_wo_alarm")
        wa = config.getint("fm", "keep_events_with_alarm")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        border = datetime.datetime.now() - datetime.timedelta(seconds=w)
        # Drop all events with event class action L
        to_drop = [c.id for c in EventClass.objects.filter(action="L")]
        dc = ActiveEvent.objects.filter(event_class__in=to_drop,
            timestamp__lte=border).count()
        if dc:
            ActiveEvent.objects.filter(event_class__in=to_drop,
                timestamp__lte=border).delete()
<<<<<<< HEAD
            self.logger.info("%d active events cleaned (requested by event class)" % dc)
=======
            self.info("%d active events cleaned (requested by event class)" % dc)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        ## Events without alarms
        if woa == 0:
            # Drop all events not contributing to alarms
            dc = ActiveEvent.objects.filter(alarms__exists=False,
                timestamp__lte=border).count()
            if dc:
                ActiveEvent.objects.filter(alarms__exists=False,
                    timestamp__lte=border).delete()
<<<<<<< HEAD
                self.logger.info("%d active events cleaned (no related alarms)" % dc)
=======
                self.info("%d active events cleaned (no related alarms)" % dc)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        ## Events with alarms
        if wa == 0:
            # Drop all events contributing to alarms
            dc = ActiveEvent.objects.filter(alarms__exists=True,
                timestamp__lte=border).count()
            if dc:
                ActiveEvent.objects.filter(alarms__exists=True,
                    timestamp__lte=border).delete()
<<<<<<< HEAD
                self.logger.info("%d active events cleaned (with related alarms)" % dc)
=======
                self.info("%d active events cleaned (with related alarms)" % dc)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Archive left events
        n = 0
        for e in ActiveEvent.objects.filter(timestamp__lte=border):
            e.mark_as_archived("Archived by fm.archive job")
            n += 1
        if n:
<<<<<<< HEAD
            self.logger.info("%d active events are moved into archive" % n)
=======
            self.info("%d active events are moved into archive" % n)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Cleanup archive
        if woa > 0:
            border = datetime.datetime.now() - datetime.timedelta(days=woa)
            dc = ArchivedEvent.objects.filter(
                alarms__exists=False, timestamp__lte=border).count()
            if dc:
                ArchivedEvent.objects.filter(
                    alarms__exists=False, timestamp__lte=border).delete()
<<<<<<< HEAD
                self.logger.info("%d archived events cleaned (no related alarms)", dc)
=======
                self.info("%d archived events cleaned (no related alarms)")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        if wa > 0:
            border = datetime.datetime.now() - datetime.timedelta(days=wa)
            dc = ArchivedEvent.objects.filter(
                alarms__exists=True, timestamp__lte=border).count()
            if dc:
                ArchivedEvent.objects.filter(
                    alarms__exists=True, timestamp__lte=border).delete()
<<<<<<< HEAD
                self.logger.info("%d archived events cleaned (with related alarms)", dc)
=======
                self.info("%d archived events cleaned (with related alarms)")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return True
