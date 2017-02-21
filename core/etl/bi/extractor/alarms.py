# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarms Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import bisect
import datetime
## NOC modules
from base import BaseExtractor
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.reboot import Reboot
from noc.sa.models.managedobject import ManagedObject
from noc.core.bi.models.alarms import Alarms
from noc.core.etl.bi.stream import Stream
from noc.lib.dateutils import total_seconds


class AlarmsExtractor(BaseExtractor):
    name = "alarms"
    extract_delay = int(os.environ.get(
        "NOC_BI_EXTRACT_DELAY_ALARMS", 3600
    ))
    clean_delay = int(os.environ.get(
        "NOC_BI_CLEAN_DELAY_ALARMS", 86400
    ))
    reboot_interval = datetime.timedelta(seconds=int(os.environ.get(
        "NOC_BI_REBOOT_INTERVAL", 60
    )))

    def __init__(self, prefix, start, stop):
        super(AlarmsExtractor, self).__init__(prefix, start, stop)
        self.alarm_stream = Stream(Alarms, prefix)

    def extract(self):
        # Get reboots
        reboots = {}  # object -> [ts1, .., tsN]
        for d in Reboot._get_collection().aggregate([
            {
                "$match": {
                    "ts": {
                        "$gt": self.start - self.reboot_interval,
                        "$lte": self.stop
                    }
                }
            },
            {
                "$sort": {
                    "ts": 1
                }
            },
            {
                "$group": {
                    "_id": "$object",
                    "reboots": {
                        "$push": "$ts"
                    }
                }
            }
        ]):
            reboots[d["_id"]] = d["reboots"]
        #
        for d in ArchivedAlarm._get_collection().find({
            "timestamp": {
                "$gt": self.start,
                "$lte": self.stop
            }
        }, timeout=False).sort("timestamp"):
            mo = ManagedObject.get_by_id(d["managed_object"])
            if not mo:
                continue
            # Process reboot data
            o_reboots = reboots.get(d["managed_object"])
            reboots = 0
            if o_reboots:
                i = bisect.bisect_left(o_reboots, d["clear_timestamp"])
                if i:
                    t0 = d["timestamp"] - self.reboot_interval
                    while i > 0 and o_reboots[i] >= t0:
                        reboots += 1
                        i -= 1
            #
            self.alarm_stream.push(
                ts=d["timestamp"],
                close_ts=d["clear_timestamp"],
                duration=max(0, int(total_seconds(d["clear_timestamp"] - d["timestamp"]))),
                alarm_id=str(d["_id"]),
                root=str(d.get("root") or ""),
                alarm_class=d["alarm_class"],
                severity=d["severity"],
                reopens=d.get("reopens") or 0,
                direct_services=sum(ss["summary"] for ss in d.get("direct_services", [])),
                direct_subscribers=sum(ss["summary"] for ss in d.get("direct_subscribers", [])),
                total_objects=sum(ss["summary"] for ss in d.get("total_objects", [])),
                total_services=sum(ss["summary"] for ss in d.get("total_services", [])),
                total_subscribers=sum(ss["summary"] for ss in d.get("total_subscribers", [])),
                escalation_ts=d.get("escalation_ts"),
                escalation_tt=d.get("escalation_tt"),
                managed_object=mo,
                pool=mo.pool,
                ip=mo.address,
                profile=mo.profile_name,
                object_profile=mo.object_profile,
                vendor=mo.vendor,
                platform=mo.platform,
                version=mo.version.version,
                administrative_domain=mo.administrative_domain,
                segment=mo.segment,
                container=mo.container,
                x=mo.x,
                y=mo.y,
                reboots=reboots
            )
            self.last_ts = d["timestamp"]
        self.alarm_stream.finish()

    def clean(self):
        ArchivedAlarm._get_collection().remove({
            "timestamp": {
                "$lte": self.clean_ts
            }
        })
