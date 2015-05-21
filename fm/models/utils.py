# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM models utils
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Third-party modules
from bson import ObjectId
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


def get_severity(alarms):
    """
    Return severity CSS class name for the alarms
    :param alarms: Single instance or list of alarms
    """
    def f(a):
        if hasattr(a, "id"):
            return a.id
        elif isinstance(a, basestring):
            return ObjectId(a)
        else:
            return a

    severity = 0
    if not isinstance(alarms, list):
        alarms = [alarms]
    al = [f(x) for x in alarms]
    for ac in (ActiveAlarm, ArchivedAlarm):
        if len(al) == 1:
            q = {"_id": al[0]}
        else:
            q = {
                "_id": {
                    "$in": al
                }
            }
        for d in ac._get_collection().find(q, {"severity": 1}):
            severity = max(severity, d["severity"])
            al.remove(d["_id"])
        if not al:
            break
    return severity
