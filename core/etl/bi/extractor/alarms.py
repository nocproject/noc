# ----------------------------------------------------------------------
# Alarms Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.reboot import Reboot
from noc.fm.models.alarmclass import AlarmClass
from noc.sa.models.managedobject import ManagedObject
from noc.bi.models.alarms import Alarms
from noc.core.etl.bi.stream import Stream
from noc.config import config
from noc.core.dateutils import hits_in_range
from noc.sa.models.serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from .archive import ArchivingExtractor


class AlarmsExtractor(ArchivingExtractor):
    name = "alarms"
    extract_delay = config.bi.extract_delay_alarms
    clean_delay = config.bi.clean_delay_alarms
    reboot_interval = datetime.timedelta(seconds=config.bi.reboot_interval)
    enable_archive = config.bi.enable_alarms_archive
    archive_batch_limit = config.bi.alarms_archive_batch_limit
    archive_collection_template = config.bi.alarms_archive_policy

    def __init__(self, prefix, start, stop, use_archive=False):
        self.use_archive = use_archive
        super().__init__(prefix, start, stop)
        self.alarm_stream = Stream(Alarms, prefix)

    def iter_data(self):
        if self.use_archive:
            coll = [
                self._archive_db.get_collection(coll_name)
                for coll_name in self.find_archived_collections(self.start, self.stop)
            ]
        else:
            coll = [ArchivedAlarm._get_collection()]
        for c in coll:
            for d in c.find(
                {"clear_timestamp": {"$gt": self.start, "$lte": self.stop}}, no_cursor_timeout=True
            ).sort("clear_timestamp"):
                yield d

    def extract(self, *args, **options):
        nr = 0
        # Get reboots
        r = Reboot._get_collection().aggregate(
            [
                {"$match": {"ts": {"$gt": self.start - self.reboot_interval, "$lte": self.stop}}},
                {"$sort": {"ts": 1}},
                {"$group": {"_id": "$object", "reboots": {"$push": "$ts"}}},
            ]
        )
        # object -> [ts1, .., tsN]
        reboots = {d["_id"]: d["reboots"] for d in r}
        for d in self.iter_data():
            mo = ManagedObject.get_by_id(d["managed_object"])
            if not mo:
                continue
            # Process reboot data
            o_reboots = reboots.get(d["managed_object"], [])
            n_reboots = hits_in_range(
                o_reboots, d["timestamp"] - self.reboot_interval, d["clear_timestamp"]
            )
            self.alarm_stream.push(
                ts=d["timestamp"],
                close_ts=d["clear_timestamp"],
                duration=max(0, int((d["clear_timestamp"] - d["timestamp"]).total_seconds())),
                alarm_id=str(d["_id"]),
                root=str(d.get("root") or ""),
                rca_type=d.get("rca_type") or 0,
                alarm_class=AlarmClass.get_by_id(d["alarm_class"]),
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
                version=mo.version,
                administrative_domain=mo.administrative_domain,
                segment=mo.segment,
                container=mo.container,
                project=mo.project,
                x=mo.x,
                y=mo.y,
                reboots=n_reboots,
                services=[
                    {
                        "profile": ServiceProfile.get_by_id(ss["profile"]).bi_id,
                        "summary": ss["summary"],
                    }
                    for ss in d.get("direct_services", [])
                ],
                subscribers=[
                    {
                        "profile": SubscriberProfile.get_by_id(ss["profile"]).bi_id,
                        "summary": ss["summary"],
                    }
                    for ss in d.get("direct_subscribers", [])
                ],
                # location=mo.container.get_address_text()
                ack_user=d.get("ack_user", ""),
                ack_ts=d.get("ack_ts"),
            )
            nr += 1
            self.last_ts = d["clear_timestamp"]
        self.alarm_stream.finish()
        return nr

    def clean(self, force=False):
        # Archive
        super().clean()
        # Clean
        if force:
            print("Clean ArchivedAlarm collection before %s" % self.clean_ts)
            ArchivedAlarm._get_collection().remove({"clear_timestamp": {"$lte": self.clean_ts}})

    @classmethod
    def get_start(cls):
        d = ArchivedAlarm._get_collection().find_one(
            {}, {"_id": 0, "timestamp": 1}, sort=[("timestamp", 1)]
        )
        if not d:
            return None
        return d.get("timestamp")

    def iter_archived_items(self):
        for d in ArchivedAlarm._get_collection().find(
            {"clear_timestamp": {"$lte": self.clean_ts}}, no_cursor_timeout=True
        ):
            yield d
