# ----------------------------------------------------------------------
# Alarms Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.sa.models.managedobject import ManagedObject
from noc.bi.models.alarmlogs import AlarmLogs
from noc.core.etl.bi.stream import Stream
from .base import BaseExtractor


class AlarmLogsExtractor(BaseExtractor):
    name = "alarmlogs"

    def __init__(self, prefix, start, stop):
        super().__init__(prefix, start, stop)
        self.alarmlogs_stream = Stream(AlarmLogs, prefix)

    def extract(self, *args, **options):
        nr = 0
        for d in ArchivedAlarm._get_collection().aggregate(
            [
                {"$match": {"log.timestamp": {"$gt": self.start, "$lte": self.stop}}},
                {"$unwind": "$log"},
                {"$match": {"log.timestamp": {"$gt": self.start, "$lte": self.stop}}},
                {
                    "$project": {
                        "alarm_timestamp": "$timestamp",
                        "alarm_clear_ts": "$clear_timestamp",
                        "managed_object": 1,
                        "alarm_class": 1,
                        "escalation_tt": 1,
                        "escalation_ts": 1,
                        "ack_user": 1,
                        "ack_ts": 1,
                        "c_ts": "$log.timestamp",
                        "from_status": "$log.from_status",
                        "to_status": "$log.to_status",
                        "message": "$log.message",
                        "source": "$log.source",
                    }
                },
                {"$sort": {"c_ts": 1}},
            ]
        ):
            mo = ManagedObject.get_by_id(d["managed_object"])
            self.alarmlogs_stream.push(
                ts=d["c_ts"],
                alarm_id=str(d["_id"]),
                alarm_ts=d["alarm_timestamp"],
                alarm_clear_ts=d["alarm_clear_ts"],
                alarm_class=AlarmClass.get_by_id(d["alarm_class"]),
                managed_object=mo,
                ack_user=d.get("ack_user", ""),
                ack_ts=d.get("ack_ts"),
                alarm_escalation_ts=d.get("escalation_ts"),
                alarm_escalation_tt=d.get("escalation_tt"),
                from_status=d["from_status"],
                to_status=d["to_status"],
                source=d.get("source", ""),
                message=d["message"],
            )
            nr += 1
            self.last_ts = d["c_ts"]
        self.alarmlogs_stream.finish()
        return nr

    @classmethod
    def get_start(cls):
        d = ArchivedAlarm._get_collection().find_one(
            {}, {"_id": 0, "timestamp": 1}, sort=[("timestamp", 1)]
        )
        if not d:
            return None
        return d.get("timestamp")
