# ---------------------------------------------------------------------
# FM models utils
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Union

# Third-party modules
from bson import ObjectId
import orjson

# NOC modules
from noc.core.clickhouse.connect import connection


def get_event(event_id):
    """
    Get event by event_id
    """
    sql = f"""select
        e.event_id as id,
        e.ts as timestamp,
        e.event_class as event_class_bi_id,
        e.managed_object as managed_object_bi_id,
        e.start_ts as start_timestamp,
        e.source, e.raw_vars, e.resolved_vars, e.vars,
        d.alarms as alarms
        from events e
        LEFT OUTER JOIN (
            SELECT event_id, groupArray(alarm_id) as alarms
            FROM disposelog
            WHERE event_id='{event_id}' AND alarm_id != ''
            GROUP BY event_id
        ) as d
        ON e.event_id == d.event_id
        where event_id='{event_id}'
        format JSON
    """
    cursor = connection()
    res = orjson.loads(cursor.execute(sql, return_raw=True))
    if res:
        return ActiveEvent.create_from_dict(res["data"][0])
    return None


def get_alarm(alarm_id) -> Union["ActiveAlarm", "ArchivedAlarm"]:
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
        elif isinstance(a, str):
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
            q = {"_id": {"$in": al}}
        for d in ac._get_collection().find(q, {"severity": 1}):
            severity = max(severity, d["severity"])
            al.remove(d["_id"])
        if not al:
            break
    return severity


# NOC modules
from .activeevent import ActiveEvent
from .activealarm import ActiveAlarm
from .archivedalarm import ArchivedAlarm
