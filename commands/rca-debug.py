# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc rca-debug
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import datetime
from collections import namedtuple
import operator
# NOC modules
from noc.core.management.base import BaseCommand
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.objectdata import ObjectData
from noc.core.config.base import config
from noc.lib.dateutils import total_seconds


Record = namedtuple("Record", [
    "timestamp", "alarm_id", "root_id",
    "managed_object", "address", "platform",
    "uplink1", "uplink2"
])


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--delta",
            type=int,
            default=60,
            help="Alarm delta"
        )
        parser.add_argument(
            "--trace",
            action="store_true",
            default=False,
            help="Trace RCA decision"
        )
        parser.add_argument(
            "alarm",
            nargs=1,
            help="Alarm ID"
        )

    def handle(self, alarm, delta, trace=False, *args, **kwargs):
        def nq(s):
            return s.split("#", 1)[0]

        try:
            a0 = ArchivedAlarm.objects.get(id=alarm[0])
        except ArchivedAlarm.DoesNotExist:
            self.die("Cannot find alarm")
        t0 = a0.timestamp - datetime.timedelta(seconds=delta)
        t1 = a0.timestamp + datetime.timedelta(seconds=delta)
        alarms = {}
        mos = list(a0.managed_object.segment.managed_objects)
        for a in ArchivedAlarm.objects.filter(
            timestamp__gte=t0,
            timestamp__lte=t1,
            managed_object__in=[o.id for o in mos]
        ):
            alarms[a.managed_object.id] = a
        # Enrich with roots

        # Get object segment data
        r = []
        for mo in mos:
            uplink1, uplink2 = "", ""
            d = ObjectData.get_by_id(mo)
            if d:
                uplinks = [ManagedObject.get_by_id(u) for u in d.uplinks]
                uplinks = [u for u in uplinks if u]
                if uplinks:
                    uplink1 = nq(uplinks.pop(0).name)
                if uplinks:
                    uplink2 = nq(uplinks.pop(0).name)
            a = alarms.get(mo.id)
            r += [Record(
                timestamp=a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a else "",
                alarm_id=a.id if a else "",
                root_id=a.root if a and a.root else "",
                managed_object=nq(mo.name),
                address=mo.address,
                platform=mo.platform,
                uplink1=uplink1,
                uplink2=uplink2
            )]
        MASK = "%19s | %24s | %24s | %16s | %15s | %20s | %16s | %16s"
        print(MASK % ("ts", "alarm", "root", "object", "address",
                      "platform", "uplink1", "uplink2"), file=self.stdout)
        for x in sorted(r, key=operator.attrgetter("timestamp")):
            print(MASK % x, file=self.stdout)
        if trace:
            print("Time range: %s -- %s" % (t0, t1), file=self.stdout)
            print("Topology RCA Window: %s" % ("%ss" % config.topology_rca_window if config.topology_rca_window else "Disabled"), file=self.stdout)
            amap = dict((a.id, a) for a in alarms.values())
            for x in sorted(r, key=operator.attrgetter("timestamp")):
                if not x.alarm_id:
                    continue
                print("@@@ %s %s %s" % (x.timestamp, x.alarm_id, x.managed_object), file=self.stdout)
                self.topology_rca(amap[x.alarm_id], alarms)
            # Dump
            for a in amap:
                if hasattr(amap[a], "_trace_root"):
                    print("%s -> %s" % (a, amap[a]._trace_root), file=self.stdout)

    def topology_rca(self, alarm, alarms, seen=None, ts=None):
        def can_correlate(a1, a2):
            return (
                not config.topology_rca_window or
                total_seconds(a1.timestamp - a2.timestamp) <= config.topology_rca_window
            )

        ts = ts or alarm.timestamp
        seen = seen or set()
        print(">>> topology_rca(%s, %s)" % (alarm.id, "{%s}" % ", ".join(str(x) for x in seen)), file=self.stdout)
        if hasattr(alarm, "_trace_root"):
            print("<<< already correlated", file=self.stdout)
            return
        if alarm.id in seen:
            print("<<< already seen", file=self.stdout)
            return  # Already correlated
        seen.add(alarm.id)
        o_id = alarm.managed_object.id
        # Get neighbor objects
        neighbors = set()
        uplinks = []
        ou = ObjectData.get_by_id(object=o_id)
        if ou and ou.uplinks:
            uplinks = ou.uplinks
            neighbors.update(uplinks)
        for du in ObjectData.get_neighbors(o_id):
            neighbors.add(du)
        if not neighbors:
            print("<<< no neighbors", file=self.stdout)
            return
        # Get neighboring alarms
        na = {}
        for n in neighbors:
            a = alarms.get(n)
            if a and a.timestamp <= ts:
                na[n] = a
        print("    Neighbor alarms: %s" % ", ".join("%s%s (%s)" % ("U:" if x in uplinks else "", na[x], ManagedObject.get_by_id(x).name) for x in na), file=self.stdout)
        print("    Uplinks: %s" % ", ".join(ManagedObject.get_by_id(u).name for u in uplinks), file=self.stdout)
        if uplinks and len([na[o] for o in uplinks if o in na]) == len(uplinks):
            # All uplinks are faulty
            # uplinks are ordered according to path length
            # Correlate with first applicable
            for u in uplinks:
                a = na[u]
                if can_correlate(alarm, a):
                    print("+++ SET ROOT %s -> %s" % (alarm.id, a.id), file=self.stdout)
                    alarm._trace_root = a.id
                    break
        # Correlate neighbors' alarms
        for d in na:
            self.topology_rca(na[d], alarms, seen, ts)
        print("<<< done", file=self.stdout)

if __name__ == "__main__":
    Command().run()
