# ---------------------------------------------------------------------
# FM models utils
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Union

# Third-party modules
from bson import ObjectId
import orjson

# NOC modules
from noc.config import config
from noc.core.clickhouse.connect import connection
from noc.core.clickhouse.fields import DateField, DateTimeField

MAX_DISPOSE_DELAY = datetime.timedelta(hours=1)


def get_event(event_id):
    event_id = str(ObjectId(event_id))
    # Determine possible date
    oid = ObjectId(event_id)
    ts: datetime.datetime = oid.generation_time.astimezone(config.timezone)
    from_ts = ts - MAX_DISPOSE_DELAY
    to_ts = ts + MAX_DISPOSE_DELAY
    """
    Get event by event_id
    """
    sql = """
        SELECT
            e.event_id as id,
            e.ts as timestamp,
            e.event_class as event_class_bi_id,
            e.managed_object as managed_object_bi_id,
            e.start_ts as start_timestamp,
            e.source, e.raw_vars, e.resolved_vars, e.vars,
            d.alarms as alarms
        FROM events e
            LEFT OUTER JOIN (
                SELECT event_id, groupArray(alarm_id) as alarms
                FROM disposelog
                WHERE
                    event_id = %s
                    AND alarm_id != ''
                    AND ts BETWEEN %s AND %s
                    AND date BETWEEN %s AND %s
                GROUP BY event_id
            ) as d
            ON e.event_id == d.event_id
        WHERE
            event_id = %s
            AND ts BETWEEN %s AND %s
            AND date BETWEEN %s AND %s
        FORMAT JSON
    """
    cursor = connection()
    df = DateField()
    dtf = DateTimeField()
    res = orjson.loads(
        cursor.execute(
            sql,
            args=[
                event_id,
                dtf.to_json(from_ts),
                dtf.to_json(to_ts),
                df.to_json(from_ts),
                df.to_json(to_ts),
                event_id,
                dtf.to_json(from_ts),
                dtf.to_json(to_ts),
                df.to_json(from_ts),
                df.to_json(to_ts),
            ],
            return_raw=True,
        )
    )
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
