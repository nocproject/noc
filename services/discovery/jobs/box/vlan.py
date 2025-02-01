# ---------------------------------------------------------------------
# Vlan check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Optional, Set, Dict

# NOC modules
from noc.services.discovery.jobs.base import PolicyDiscoveryCheck
from noc.vc.models.l2domain import L2Domain
from noc.vc.models.vlan import VLAN
from noc.inv.models.resourcepool import ResourcePool
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import list_to_ranges
from noc.config import config


@dataclass
class DiscoveryVLAN(object):
    id: int
    l2domain: "L2Domain"
    name: Optional[str] = None
    description: Optional[str] = None
    allow_allocate: bool = False
    allow_seen: bool = True


class VLANCheck(PolicyDiscoveryCheck):
    """
    VLAN discovery
    """

    name = "vlan"
    required_script = "get_vlans"
    # @todo: required_capabilities = ?

    VLAN_QUERY = """(
        Match("virtual-router", vr, "forwarding-instance", fi, "vlans", vlan) or
        Match("virtual-router", vr, "forwarding-instance", fi, "vlans", vlan, "name", name)
    ) and Group("vlan")"""

    @staticmethod
    def is_enabled_for_object(oo):
        return (
            oo.object_profile.vlan_interface_discovery != "D"
            or oo.object_profile.vlan_vlandb_discovery != "D"
        )

    def handler(self):
        self.logger.info("Checking VLANs")
        object_l2domain: Optional["L2Domain"] = self.object.get_effective_l2_domain()
        if not object_l2domain:
            self.logger.info("L2Domain for object is not set. Skipping")
            return
        if object_l2domain.get_vlan_discovery_policy() == "D":
            self.logger.info(
                "VLAN discovery is disabled for l2domain '%s'. Skipping...",
                self.object.l2_domain.name,
            )
            return
        # Get list of VLANs from equipment
        object_vlans = self.get_object_vlans(object_l2domain)
        interface_vlans = self.get_interface_vlans(object_l2domain)
        # Merge with artifactory ones
        collected_vlans = self.merge_vlans(object_vlans + interface_vlans)
        # Check we have collected any VLAN
        if not collected_vlans:
            self.logger.info("No any VLAN collected. Skipping")
            return
        # Refresh vlans in database
        ensured_vlans = self.ensure_vlans(collected_vlans)
        # Refresh discovery timestamps
        self.refresh_discovery_timestamps(ensured_vlans)
        # Send "seen" events
        self.send_seen_events(ensured_vlans)
        # self.update_caps(
        #     {"DB | VLANs": VLAN.objects.filter(sources__managed_object=self.object)},
        #     source="vlan",
        # )

    def allocate_vlans(self, l2_domain: "L2Domain", vlans: List["DiscoveryVLAN"]) -> List["VLAN"]:
        """
        1. Getting pools
        3. Lock by pool
        4. Allocate VLANs (separate method) if condition - create. Param sync_vlans
        """
        pools = [p.pool for p in l2_domain.iter_pool_settings()]
        # @todo Filter pool by allocate vland + pool filter
        vlan_include_filter: Set[int] = set(l2_domain.get_effective_vlan_id())
        # Check VLANs for create
        create_vlans = []
        for dvlan in vlans:
            if not dvlan.allow_allocate:
                self.logger.debug("[%d] Not allowed to allocated by policy", dvlan.id)
                continue
            if vlan_include_filter and dvlan.id not in vlan_include_filter:
                self.logger.debug("[%d] Not allowed l2domain include filter", dvlan.id)
                continue
            create_vlans.append(dvlan)
        if not create_vlans:
            return []
        # Create VLAN
        r = []
        if not pools:
            for dvlan in create_vlans:
                avlan = VLAN.from_template(l2_domain=l2_domain, vlan_id=dvlan.id, name=dvlan.name)
                if avlan:
                    avlan.__allow_seen = dvlan.allow_seen
                    avlan.save()
                    r.append(avlan)
            self.logger.info(
                "[%s] Create VLANs: %s", l2_domain.name, list_to_ranges([v.vlan for v in r])
            )
            return r
        with ResourcePool.acquire(
            pools, owner=f"discovery-{config.pool}-{getattr(self.service, 'slot_number', '')}"
        ):
            for dvlan in create_vlans:
                self.logger.info("[%s|%s] Create VLAN", l2_domain.name, dvlan.id)
                avlan = VLAN.from_template(l2_domain=l2_domain, vlan_id=dvlan.id, name=dvlan.name)
                if avlan:
                    avlan.__allow_seen = dvlan.allow_seen
                    r.append(avlan)
                    avlan.save()
                self.logger.info(
                    "[%s] Create VLANs: %s", l2_domain.name, list_to_ranges([v.vlan for v in r])
                )
        return r

    def ensure_vlans(self, vlans: List["DiscoveryVLAN"]) -> List["VLAN"]:
        """
        Synchronize all vlans
        Get existing VLAN
        2. Getting vlans
        5. Return VLANs
        """
        result: List["VLAN"] = []
        l2domains_vlan_map: Dict["L2Domain", Dict[int, "DiscoveryVLAN"]] = {}
        for v in vlans:
            if v.l2domain not in l2domains_vlan_map:
                l2domains_vlan_map[v.l2domain] = {}
            l2domains_vlan_map[v.l2domain][v.id] = v
        for l2domain, vlanid_map in l2domains_vlan_map.items():
            processed_vlans = set()
            for vlan in VLAN.objects.filter(l2_domain=l2domain, vlan__in=list(vlanid_map)):
                processed_vlans.add(vlan.vlan)
                # @todo fix for some intelligence
                vlan.__allow_seen = vlanid_map[vlan.vlan].allow_seen
            allocated_vlans: Set[int] = set(vlanid_map) - processed_vlans
            if allocated_vlans:
                result += self.allocate_vlans(l2domain, [vlanid_map[av] for av in allocated_vlans])
        return result

    def get_object_vlans(self, l2_domain: "L2Domain") -> List["DiscoveryVLAN"]:
        """Get VLANs from equipment"""
        if self.object.object_profile.vlan_vlandb_discovery == "D":
            self.logger.info(
                "VLAN Database Discovery is disabled by Managed Object Profile policy. Skipping..."
            )
            return []
        self.logger.info("[%s] Collecting VLANs", l2_domain.name)
        obj_vlans = self.get_data() or []
        vlan_filter = l2_domain.get_vlan_discovery_filter()
        if vlan_filter:
            vlan_filter = set(vlan_filter.include_vlans)
        allow_allocate = (
            l2_domain.get_vlan_discovery_policy() == "E"
            and self.object.object_profile.vlan_vlandb_discovery in {"V", "C"}
        )
        return [
            DiscoveryVLAN(
                id=v["vlan_id"],
                l2domain=l2_domain,
                name=v.get("name"),
                allow_allocate=allow_allocate,
                allow_seen=self.object.object_profile.vlan_vlandb_discovery in {"S", "V"},
            )
            for v in obj_vlans
            if not vlan_filter or v["vlan_id"] in vlan_filter
        ]

    def get_interface_vlans(self, l2_domain: "L2Domain") -> List["DiscoveryVLAN"]:
        """Get VLANs from interface discovery artifact"""
        self.logger.debug("Getting interface vlans")
        if self.object.object_profile.vlan_interface_discovery == "D":
            self.logger.info(
                "VLAN Interface Discovery is disabled by Managed Object Profile policy. Skipping..."
            )
            return []
        vlans = self.get_artefact("interface_assigned_vlans")
        if not vlans:
            self.logger.info("No interface_assigned_vlans artefact, skipping interface vlans")
            return []
        vlan_filter = l2_domain.get_vlan_discovery_filter()
        if vlan_filter:
            vlan_filter = set(vlan_filter.include_vlans)
        allow_allocate = (
            l2_domain.get_vlan_discovery_policy() == "E"
            and self.object.object_profile.vlan_interface_discovery in {"V", "C"}
        )
        return [
            DiscoveryVLAN(
                id=v,
                l2domain=l2_domain,
                allow_allocate=allow_allocate,
                allow_seen=self.object.object_profile.vlan_interface_discovery in {"S", "V"},
            )
            for v in vlans
            if not vlan_filter or v in vlan_filter
        ]

    @staticmethod
    def merge_vlans(vlans: List["DiscoveryVLAN"]) -> List["DiscoveryVLAN"]:
        """
        Merge object vlans with artifactory ones
        :param vlans:
        :return:
        """
        r = []
        processed = []
        for v in vlans:
            if v.id in processed:
                continue
            r.append(v)
            processed.append(v.id)
        return vlans

    def refresh_discovery_timestamps(self, vlans: List["VLAN"]):
        """
        Bulk update discovery timestamps of all vlans from list
        :param vlans: List of VLAN instances
        :return: None
        """
        bulk = []
        for vlan in vlans:
            vlan.touch(bulk)
        if bulk:
            self.logger.info("Bulk update %d timestamps", len(bulk))
            VLAN._get_collection().bulk_write(bulk, ordered=True)

    @staticmethod
    def send_seen_events(vlans: List["VLAN"]):
        """
        Send *seen* event to all vlans from list
        :param vlans: List of VLAN instances
        :return: None
        """
        for vlan in vlans:
            if vlan.__allow_seen:
                vlan.fire_event("seen")

    def get_policy(self) -> str:
        return self.object.get_vlan_discovery_policy()

    def get_data_from_script(self):
        return self.object.scripts.get_vlans()

    def get_data_from_confdb(self):
        r = [
            {"vlan_id": d["vlan"], "name": d.get("name", "VLAN %s" % d["vlan"])}
            for d in self.confdb.query(self.VLAN_QUERY)
        ]
        return IGetVlans().clean_result(r)
