# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alarms Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import bisect
import datetime
# NOC modules
from base import BaseExtractor
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.reboot import Reboot
from noc.sa.models.managedobject import ManagedObject
from noc.bi.models.alarms import Alarms
from noc.core.etl.bi.stream import Stream
from noc.lib.dateutils import total_seconds
from noc.config import config
from noc.lib.dateutils import hits_in_range


class AlarmsExtractor(BaseExtractor):
    name = "alarms"
    extract_delay = config.bi.extract_delay_alarms
    clean_delay = config.bi.clean_delay_alarms
    reboot_interval = datetime.timedelta(seconds=config.bi.reboot_interval)

    def __init__(self, prefix, start, stop):
        super(AlarmsExtractor, self).__init__(prefix, start, stop)
        self.alarm_stream = Stream(Alarms, prefix)

    def extract(self):
        # Get reboots
        reboots = {}  # object -> [ts1, .., tsN]
        r = Reboot._get_collection().aggregate([
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
        ])
        if r["ok"]:
            reboots = dict((d["_id"], d["reboots"]) for d in r["result"])
        #
        for d in ArchivedAlarm._get_collection().find({
            "clear_timestamp": {
                "$gt": self.start,
                "$lte": self.stop
            }
        }, timeout=False).sort("timestamp"):
            mo = ManagedObject.get_by_id(d["managed_object"])
            if not mo:
                continue
            # Process reboot data
            o_reboots = reboots.get(d["managed_object"], [])
            n_reboots = hits_in_range(
                o_reboots,
                d["timestamp"] - self.reboot_interval,
                d["clear_timestamp"]
            )
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
                profile=mo.profile,
                object_profile=mo.object_profile,
                vendor=mo.vendor,
                platform=mo.platform,
                version=mo.version.version,
                administrative_domain=mo.administrative_domain,
                segment=mo.segment,
                container=mo.container,
                x=mo.x,
                y=mo.y,
                reboots=n_reboots
            )
            self.last_ts = d["timestamp"]
        self.alarm_stream.finish()

    def clean(self):
        ArchivedAlarm._get_collection().remove({
            "timestamp": {
                "$lte": self.clean_ts
            }
        })
