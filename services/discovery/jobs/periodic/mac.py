# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MAC Check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
from functools import reduce
from collections import defaultdict

# Third-party modules
import six
from typing import Tuple, List, DefaultDict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.perf import metrics
from noc.core.mac import MAC
from noc.inv.models.discoveryid import DiscoveryID


class MACCheck(DiscoveryCheck):
    """
    MAC discovery
    """

    name = "mac"
    required_script = "get_mac_address_table"
    XMAC_POLICIES = ("i", "c", "C")
    XMAC_FILTER_TYPE = {"D", "S"}  # Only Dynamic and Static MAC collected

    def handler(self):
        # Build filter policy
        if self.object.object_profile.mac_collect_all:
            mf = self.filter_all
        else:
            mf = []
            self.allowed_vlans = set()
            # Filter by interface profile
            if self.object.object_profile.mac_collect_interface_profile:
                mf += [self.filter_interface_profile]
            # Filter by management vlan
            if self.object.object_profile.mac_collect_management:
                vlan = self.object.segment.get_management_vlan()
                if vlan:
                    self.allowed_vlans.add(vlan)
            # Filter by multicast vlan
            if self.object.object_profile.mac_collect_multicast:
                vlan = self.object.segment.get_multicast_vlan()
                if vlan:
                    self.allowed_vlans.add(vlan)
            # Filter by VC Filter (not implemented yet)
            if self.object.object_profile.mac_collect_vcfilter:
                self.logger.info("VC Filters are not implemented yet")
            # Apply VLAN filter
            if self.allowed_vlans:
                mf += [self.filter_vlan]
            if not mf:
                self.logger.info("MAC collection is not enabled by any policy")
                return
            mf = reduce(lambda x, y: x or y, mf)
        # Collect macs
        now = time.localtime()
        date = time.strftime("%Y-%m-%d", now)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", now)
        unknown_interfaces = set()
        total_macs = 0
        data = []
        mo_bi_id = self.object.bi_id
        seg_bi_id = self.object.segment.bi_id
        collect_if_objects = self.object.enable_autosegmentation
        if_mac = defaultdict(set)  # interface -> [macs]
        # Collect and process MACs
        mac_direct_downlink = defaultdict(list)  # type: DefaultDict[str, List[MAC]]
        mac_downlink_policy = tuple()  # type: Tuple[str, ...]
        if self.object.object_profile.enable_box_discovery_xmac:
            mac_downlink_policy = self.XMAC_POLICIES
        result = self.object.scripts.get_mac_address_table()
        for v in result:
            total_macs += 1
            if v["type"] not in self.XMAC_FILTER_TYPE or not v["interfaces"]:
                self.logger.debug("Ignored not dynamic or static MAC: %s" % v["mac"])
                continue
            ifname = str(v["interfaces"][0])
            iface = self.get_interface_by_name(ifname)
            if not iface:
                unknown_interfaces.add(ifname)
                continue  # Interface not found
            ifprofile = iface.get_profile()
            mac = MAC(v["mac"])
            if mac_downlink_policy and ifprofile.mac_discovery_policy in mac_downlink_policy:
                mac_direct_downlink[ifname] += [mac]
            if collect_if_objects:
                if_mac[iface].add(v["mac"])
            if not mf(iface, v["vlan_id"], v["mac"]):
                self.logger.debug(
                    "Filtered: Iface: %s, Vlan: %s, MAC: %s" % (iface, v["vlan_id"], v["mac"])
                )
                continue
            data += [
                {
                    "date": date,
                    "ts": ts,
                    "managed_object": mo_bi_id,
                    "mac": int(mac),
                    "interface": ifname,
                    "interface_profile": ifprofile.bi_id,
                    "segment": seg_bi_id,
                    "vlan": v.get("vlan_id", 0),
                    "is_uni": 1 if ifprofile.is_uni else 0,
                }
            ]
        if unknown_interfaces:
            self.logger.info("Ignoring unknown interfaces: %s", ", ".join(unknown_interfaces))
        processed_macs = len(data)
        metrics["discovery_mac_total_macs"] += total_macs
        metrics["discovery_mac_processed_macs"] += processed_macs
        metrics["discovery_mac_ignored_macs"] += total_macs - processed_macs
        if data:
            self.logger.info("%d MAC addresses are collected. Sending", processed_macs)
            self.service.register_metrics("mac", data)
            if collect_if_objects:
                self.build_seen_objects(if_mac)
        else:
            self.logger.info("No MAC addresses collected")
        if mac_direct_downlink:
            self.job.set_artefact("mac_direct_downlink", mac_direct_downlink)

    def filter_all(self, interface, vlan, mac):
        return True

    def filter_interface_profile(self, interface, vlan, mac):
        return interface.get_profile().mac_discovery_policy != "d"

    def filter_vlan(self, interface, vlan, mac):
        return vlan in self.allowed_vlans

    def build_seen_objects(self, if_mac):
        """
        Build seen_objects artefact
        :param if_mac: interface -> [macs]
        :return: interface -> [managed objects]
        """
        # Resolve MACs
        all_macs = reduce(lambda x, y: x | y, six.itervalues(if_mac))
        mmap = DiscoveryID.find_objects(all_macs)
        if not mmap:
            self.logger.info("Cannot build seen_objects artefact: Cannot resolve any MACs")
            return
        # Bind resolved MACs to interfaces
        seen_objects = defaultdict(set)  # interface -> [ManagedObject]
        for iface in if_mac:
            rr = set(mmap[m] for m in if_mac[iface] if m in mmap)
            if rr:
                seen_objects[iface] = rr
        # Update artifact
        current = self.get_artefact("seen_objects") or {}
        current.update(seen_objects)
        self.set_artefact("seen_objects", current)
