# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Segment MAC discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.core.clickhouse.connect import connection
from noc.core.mac import MAC
from noc.inv.models.discoveryid import DiscoveryID


class MACDiscoveryCheck(TopologyDiscoveryCheck):
    name = "mac"

    MAC_WINDOW = 2 * 86400

    def __init__(self, job):
        super(TopologyDiscoveryCheck, self).__init__(job)

    def handler(self):
        self.logger.info("Checking %s topology", self.name)
        # Get segment hierarchy
        segments = set(self.object.get_nested_ids())
        # Get managed objects and id <-> bi_id mappings
        bi_map = {}  # bi_id -> mo
        for mo in ManagedObject.objects.filter(
                segment__in=[str(x) for x in segments]
        ):
            bi_map[str(mo.bi_id)] = mo
        # Fetch latest MAC tables snapshots from ClickHouse
        # @todo: Apply vlan restrictions
        t0 = datetime.datetime.now() - datetime.timedelta(seconds=self.MAC_WINDOW)
        t0 = t0.replace(microsecond=0)
        SQL = """SELECT managed_object, mac, max(ts), argMax(interface, ts)
        FROM mac
        WHERE
          date >= toDate('%s')
          AND ts >= toDateTime('%s')
          AND managed_object IN (%s)
        GROUP BY ts, managed_object, mac
        ORDER BY ts
        """ % (t0.date().isoformat(), t0.isoformat(sep=" "),
               ", ".join(bi_map))
        ch = connection()
        # Fill FIB
        mtable = []  # mo_id, mac, iface, ts
        last_ts = {}  # mo -> ts
        for mo_bi_id, mac, ts, iface in ch.execute(post=SQL):
            mo = bi_map.get(mo_bi_id)
            if mo:
                mtable += [[mo, MAC(int(mac)), iface, ts]]
                last_ts[mo] = max(ts, last_ts.get(mo, ts))
        # Filter out aged MACs
        mtable = [m for m in mtable if m[3] == last_ts[m[0]]]
        # Resolve objects
        macs = set(x[1] for x in mtable)
        if not macs:
            self.logger.info("No MAC addresses collected. Stopping")
            return
        object_macs = DiscoveryID.find_objects(macs)
        if not object_macs:
            self.logger.info("Cannot resolve any MAC addresses. Stopping")
            return
        # Build FIB
        fib = {}  # object -> interface -> {seen objects}
        for mo, mac, iface, ts in mtable:
            ro = object_macs.get(mac)
            if not ro:
                continue
            if mo not in fib:
                fib[mo] = {}
            if iface in fib[mo]:
                fib[mo][iface].add(ro)
            else:
                fib[mo][iface] = set([ro])
        # Find uplinks and coverage
        coverage = {}  # mo -> covered objects
        uplinks = {}  # mo -> uplink interface
        up_fib = {}  # mo -> {seen via uplinks}
        for mo in fib:
            coverage[mo] = set([mo])
            for iface in fib[mo]:
                if self.is_uplink(mo, fib[mo][iface], segments):
                    uplinks[mo] = iface
                    up_fib[mo] = fib[mo][iface]
                else:
                    coverage[mo] |= fib[mo][iface]
            if mo not in uplinks:
                self.logger.info(
                    "[%s] Cannot detect uplinks. Topology may be imprecise",
                    mo.name
                )
        # Dump FIB
        if self.logger.isEnabledFor(logging.DEBUG):
            for mo in fib:
                self.logger.debug("%s:", mo.name)
                if mo in uplinks:
                    self.logger.debug("  * %s: %s", uplinks[mo], ", ".join(x.name for x in up_fib[mo]))
                else:
                    self.logger.debug("    Warning: No uplinks. Topology may be imprecise")
                for iface in fib[mo]:
                    self.logger.debug("    %s: %s", iface, ", ".join(x.name for x in fib[mo][iface]))
        # Build topology
        for mo in fib:
            for iface in fib[mo]:
                if iface == uplinks.get(mo):
                    continue
                for ro in fib[mo][iface]:
                    cvr = coverage.get(ro)
                    if not cvr:
                        cvr = set([ro])
                        coverage[ro] = cvr
                    if not fib[mo][iface] - cvr:
                        # All objects from mo:iface are seen via ro
                        uplink = uplinks.get(ro)
                        if uplink:
                            self.confirm_link(mo, iface, ro, uplink)
                            break
                        else:
                            self.logger.info(
                                "[%s] No uplinks. Cannot link to %s:%s. Topology may be imprecise",
                                ro.name, mo.name, iface
                            )

    def is_preferable_over(self, link):
        segments = link.segments
        if len(segments) > 1:
            # @todo: Order segments, most specific first
            pass
        return segments[0].profile.is_preferable_method(self.name, link.discovery_method)

    def is_uplink(self, mo, if_fib, segments):
        """
        Check if if_fib belongs to uplink interface
        :param mo: managed object instance
        :param if_fib: set of managed object seen via interface
        :param segments: Set of segment ids belonging to segment tree
        :return: True, if uplink, False otherwise
        """
        for ro in if_fib:
            # Check if objects belong to same segment
            if ro.segment.id == mo.segment.id:
                continue  # Same segment, no preference
            # Check if object is outside of segment tree
            if ro.segment.id not in segments:
                return True  # Leads outside of segment tree
            # Check if ro's segment is ancestor of mo's one
            if ro.segment.id in mo.segment.get_path():
                return True
            # Compare object's levels
            if ro.object_profile.level > mo.object_profile.level:
                return True
        return False
