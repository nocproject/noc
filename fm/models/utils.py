# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM models utils
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from activeevent import ActiveEvent
from archivedevent import ArchivedEvent
from failedevent import FailedEvent
from newevent import NewEvent
from activealarm import ActiveAlarm
from archivedalarm import ArchivedAlarm


def get_event(event_id):
        """
        Get event by event_id
        """
        for ec in (ActiveEvent, ArchivedEvent, FailedEvent, NewEvent):
            e = ec.objects.filter(id=event_id).first()
            if e:
                return e
        return None


def get_alarm(alarm_id):
        """
        Get alarm by alarm_id
        """
        for ac in (ActiveAlarm, ArchivedAlarm):
            a = ac.objects.filter(id=alarm_id).first()
            if a:
                return a
        return None
