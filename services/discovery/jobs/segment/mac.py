# ----------------------------------------------------------------------
# Segment MAC discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
import enum
from typing import Set

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.core.clickhouse.connect import connection
from noc.core.mac import MAC
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.networksegment import NetworkSegment


class UplinkMethod(enum.IntEnum):
    OUTSIDE_SEGMENT = 4  # object is outside of segment tree
    OBJECT_LEVEL = 3  # Compare object's levels
    ANCESTOR_SEGMENT = 2  # Check if ro's segment is ancestor
    SAME_SEGMENT_LEVEL = 1  # compare level objects belong to same segment
    NONE = 0


class MACDiscoveryCheck(TopologyDiscoveryCheck):
    name = "mac"

    MAC_WINDOW = 2 * 86400

    def __init__(self, job):
        super().__init__(job)

    def handler(self):
        self.logger.info("Checking %s topology", self.name)
        # Get segment hierarchy
        segments = set(self.object.get_nested_ids())
        # Get managed objects and id <-> bi_id mappings
        bi_map = {}  # bi_id -> mo
        for mo in ManagedObject.objects.filter(segment__in=[str(x) for x in segments]):
            bi_map[str(mo.bi_id)] = mo
        if not bi_map:
            self.logger.info("Empty segment tree. Skipping")
            return
        # Fetch latest MAC tables snapshots from ClickHouse
        # @todo: Apply vlan restrictions
        t0 = datetime.datetime.now() - datetime.timedelta(seconds=self.MAC_WINDOW)
        t0 = t0.replace(microsecond=0)
        SQL = """SELECT managed_object, mac, argMax(ts, ts), argMax(interface, ts)
        FROM mac
        WHERE
          date >= toDate('%s')
          AND ts >= toDateTime('%s')
          AND managed_object IN (%s)
        GROUP BY ts, managed_object, mac
        """ % (
            t0.date().isoformat(),
            t0.isoformat(sep=" "),
            ", ".join(bi_map),
        )
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
        macs = {x[1] for x in mtable}
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
            if not ro or ro == mo:
                continue
            if mo not in fib:
                fib[mo] = {}
            if iface in fib[mo]:
                fib[mo][iface].add(ro)
            else:
                fib[mo][iface] = {ro}
        # Find uplinks and coverage
        coverage = {}  # mo -> covered objects
        uplinks = {}  # mo -> uplink interface
        up_fib = {}  # mo -> {seen via uplinks}
        for mo in fib:
            coverage[mo] = {mo}
            max_weight = 0
            for iface in fib[mo]:
                uplink_weight = self.get_uplink_weight(mo, fib[mo][iface], segments)
                if uplink_weight > max_weight:
                    self.logger.info("[%s] Set uplink to %s", mo, iface)
                    uplinks[mo] = iface
                    up_fib[mo] = fib[mo][iface]
                    max_weight = uplink_weight
                else:
                    coverage[mo] |= fib[mo][iface]
            if mo not in uplinks:
                self.logger.info("[%s] Cannot detect uplinks. Topology may be imprecise", mo.name)
        # Dump FIB
        if self.logger.isEnabledFor(logging.DEBUG):
            for mo in fib:
                self.logger.debug("%s:", mo.name)
                if mo in uplinks:
                    self.logger.debug(
                        "  * %s: %s", uplinks[mo], ", ".join(x.name for x in up_fib[mo])
                    )
                else:
                    self.logger.debug("    Warning: No uplinks. Topology may be imprecise")
                for iface in fib[mo]:
                    self.logger.debug(
                        "    %s: %s", iface, ", ".join(x.name for x in fib[mo][iface])
                    )
        self.logger.info("Build segment topology topology")
        # Build topology
        for mo in fib:
            for iface in fib[mo]:
                if iface == uplinks.get(mo):
                    # Filter interface that semgent uplink (linked it from upper segment discovery)
                    self.logger.debug("[%s|%s] Interface is segment uplink. Skipping..", mo, iface)
                    continue
                for ro in fib[mo][iface]:
                    cvr = coverage.get(ro)
                    if not cvr:
                        cvr = {ro}
                        coverage[ro] = cvr
                    if not fib[mo][iface] - cvr:
                        # All objects from mo:iface are seen via ro
                        self.logger.debug(
                            "[%s|%s] All objects from mo:iface are seen via ro: %s", mo, iface, ro
                        )
                        uplink = uplinks.get(ro)
                        if uplink:
                            # @todo lacp
                            self.confirm_link(mo, iface, ro, uplink)
                            break
                        self.logger.info(
                            "[%s] No uplinks. Cannot link to %s:%s. Topology may be imprecise",
                            ro.name,
                            mo.name,
                            iface,
                        )

    def get_uplink_weight(
        self, mo: ManagedObject, if_fib: Set[ManagedObject], segments: Set[NetworkSegment]
    ) -> int:
        """
        Check if if_fib belongs to uplink interface and return weght by method
        :param mo: managed object instance
        :param if_fib: set of managed object seen via interface
        :param segments: Set of segment ids belonging to segment tree
        :return: True, if uplink, False otherwise
        """
        for ro in if_fib:
            # Check if objects belong to same segment
            if ro.segment.id == mo.segment.id:
                if ro.object_profile.level > mo.object_profile.level:
                    self.logger.debug("[%s|%s] Uplink by same segment and diff level", mo, if_fib)
                    return UplinkMethod.SAME_SEGMENT_LEVEL  # Same segment, compare object's levels
                continue  # Same segment, no preference
            # Check if ro's segment is ancestor of mo's one
            if ro.segment.id in mo.segment.get_path():
                self.logger.debug("[%s|%s] Uplink by ancestor mo", mo, if_fib)
                return UplinkMethod.ANCESTOR_SEGMENT
            # Compare object's levels
            if ro.object_profile.level > mo.object_profile.level:
                self.logger.debug("[%s|%s] Uplink by object level mo", mo, if_fib)
                return UplinkMethod.OBJECT_LEVEL
            # Check if object is outside of segment tree
            # Worked if Segment has not nested, otherwise make mistakes when detect uplink device
            if ro.segment.id not in segments:
                self.logger.debug("[%s|%s] Uplink by outside segment tree", mo, if_fib)
                return UplinkMethod.OUTSIDE_SEGMENT  # Leads outside of segment tree
        return UplinkMethod.NONE
