# ----------------------------------------------------------------------
# ./noc rca-debug
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import namedtuple
import operator

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.config import config


Record = namedtuple(
    "Record",
    [
        "timestamp",
        "alarm_id",
        "root_id",
        "managed_object",
        "address",
        "platform",
        "uplink1",
        "uplink2",
    ],
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--delta", type=int, default=60, help="Alarm delta")
        parser.add_argument(
            "--trace", action="store_true", default=False, help="Trace RCA decision"
        )
        parser.add_argument("alarm", nargs=1, help="Alarm ID")

    def handle(self, alarm, delta, trace=False, *args, **kwargs):
        def nq(s):
            return s.split("#", 1)[0]

        connect()
        try:
            a0 = ArchivedAlarm.objects.get(id=alarm[0])
        except ArchivedAlarm.DoesNotExist:
            self.die("Cannot find alarm")
        t0 = a0.timestamp - datetime.timedelta(seconds=delta)
        t1 = a0.timestamp + datetime.timedelta(seconds=delta)
        alarms = {}
        mos = list(a0.managed_object.segment.managed_objects)
        for a in ArchivedAlarm.objects.filter(
            timestamp__gte=t0, timestamp__lte=t1, managed_object__in=[o.id for o in mos]
        ):
            alarms[a.managed_object.id] = a
        # Enrich with roots

        # Get object segment data
        r = []
        for mo in mos:
            uplink1, uplink2 = "", ""
            if mo.uplinks:
                uplinks = [ManagedObject.get_by_id(u) for u in mo.uplinks]
                uplinks = [u for u in uplinks if u]
                if uplinks:
                    uplink1 = nq(uplinks.pop(0).name)
                if uplinks:
                    uplink2 = nq(uplinks.pop(0).name)
            a = alarms.get(mo.id)
            r += [
                Record(
                    timestamp=a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a else "",
                    alarm_id=a.id if a else "",
                    root_id=a.root if a and a.root else "",
                    managed_object=nq(mo.name),
                    address=mo.address,
                    platform=mo.platform,
                    uplink1=uplink1,
                    uplink2=uplink2,
                )
            ]
        MASK = "%19s | %24s | %24s | %16s | %15s | %20s | %16s | %16s"
        self.print(
            MASK % ("ts", "alarm", "root", "object", "address", "platform", "uplink1", "uplink2")
        )
        for x in sorted(r, key=operator.attrgetter("timestamp")):
            self.print(MASK % x)
        if trace:
            self.print("Time range: %s -- %s" % (t0, t1))
            self.print(
                "Topology RCA Window: %s"
                % (
                    "%ss" % config.correlator.topology_rca_window
                    if config.correlator.topology_rca_window
                    else "Disabled"
                )
            )
            amap = {a.id: a for a in alarms.values()}
            for x in sorted(r, key=operator.attrgetter("timestamp")):
                if not x.alarm_id:
                    continue
                self.print("@@@ %s %s %s" % (x.timestamp, x.alarm_id, x.managed_object))
                self.topology_rca(amap[x.alarm_id], alarms)
            # Dump
            for a in amap:
                if hasattr(amap[a], "_trace_root"):
                    self.print("%s -> %s" % (a, amap[a]._trace_root))

    def topology_rca(self, alarm, alarms, ts=None):
        def can_correlate(a1, a2):
            """
            Check if alarms can be correlated together (within corellation window)
            :param a1:
            :param a2:
            :return:
            """
            return (
                not config.correlator.topology_rca_window
                or (a1.timestamp - a2.timestamp).total_seconds()
                <= config.correlator.topology_rca_window
            )

        def all_uplinks_failed(a1):
            """
            Check if all uplinks for alarm is failed
            :param a1:
            :return:
            """
            if not a1.uplinks:
                return False
            return sum(1 for mo in a1.uplinks if mo in alarms) == len(a1.uplinks)

        def get_root(a1):
            """
            Get root cause for failed uplinks.
            Considering all uplinks are failed.
            Uplinks are ordered according to path length.
            Return first applicable

            :param a1:
            :return:
            """
            for u in a1.uplinks:
                na = alarms[u]
                if can_correlate(a1, na):
                    return na
            return None

        def iter_downlink_alarms(a1):
            """
            Yield all downlink alarms
            :param a1:
            :return:
            """
            imo = a1.managed_object.id
            for ina in alarms.values():
                if ina.uplinks and imo in ina.uplinks:
                    yield ina

        def correlate(a1):
            """
            Correlate with uplink alarms if all uplinks are faulty.
            :param a1:
            :return:
            """
            if not all_uplinks_failed(a1):
                return
            a2 = get_root(a1)
            if a2:
                self.print("+++ SET ROOT %s -> %s" % (a1.id, a2.id))
                a1._trace_root = a2.id

        ts = ts or alarm.timestamp
        self.print(">>> topology_rca(%s)" % alarm.id)
        if hasattr(alarm, "_trace_root"):
            self.print("<<< already correlated")
            return
        # Get neighboring alarms
        na = {}
        uplinks = set()
        mo = alarm.managed_object.id
        for n in alarms:
            a = alarms.get(n)
            if a and a.timestamp <= ts and mo in a.rca_neighbors:
                na[n] = a
                uplinks |= set(a.uplinks)
        self.print(
            "    Neighbor alarms: %s"
            % ", ".join(
                "%s%s (%s)" % ("U:" if x in uplinks else "", na[x], ManagedObject.get_by_id(x).name)
                for x in na
            )
        )
        self.print("    Uplinks: %s" % ", ".join(ManagedObject.get_by_id(u).name for u in uplinks))
        # Correlate current alarm
        correlate(alarm)
        # Correlate all downlink alarms
        for a in iter_downlink_alarms(alarm):
            correlate(a)
        self.print("<<< done")


if __name__ == "__main__":
    Command().run()
