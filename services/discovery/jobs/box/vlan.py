# ---------------------------------------------------------------------
# Vlan check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Optional, Dict

# NOC modules
from noc.services.discovery.jobs.base import PolicyDiscoveryCheck
from noc.vc.models.l2domain import L2Domain
from noc.vc.models.vlan import VLAN
from noc.core.perf import metrics
from noc.sa.interfaces.igetvlans import IGetVlans


@dataclass
class DiscoveryVLAN(object):
    id: int
    l2domain: "L2Domain"
    name: Optional[str] = None
    description: Optional[str] = None


class VLANCheck(PolicyDiscoveryCheck):
    """
    VLAN discovery
    """

    name = "vlan"
    required_script = "get_vlans"
    # @todo: required_capabilities = ?
    # Fetch all segment VLANs if exceeded
    FULL_VLANS_THRESHOLD = 50

    VLAN_QUERY = """(
        Match("virtual-router", vr, "forwarding-instance", fi, "vlans", vlan) or
        Match("virtual-router", vr, "forwarding-instance", fi, "vlans", vlan, "name", name)
    ) and Group("vlan")"""

    def handler(self):
        self.logger.info("Checking VLANs")
        object_l2domain: Optional["L2Domain"] = self.object.l2_domain
        if object_l2domain.get_vlan_discovery_policy() == "D":
            self.logger.info(
                "VLAN discovery is disabled for l2domain '%s'. Skipping", self.object.l2_domain.name
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

    def ensure_vlans(self, vlans: List["DiscoveryVLAN"]) -> List["VLAN"]:
        """
        Refresh VLAN status in database, create when necessary
        :param vlans:
        :return:
        """
        # Get existing VLAN
        # 1. Getting pools
        # 2. Getting vlans
        # 3. Lock by pool
        # 4. Allocate VLANs (separate method) if condition - create. Param sync_vlans
        # 5. Return VLANs
        return []

    def get_default_vlan_name(self, vlan_id):
        """
        Generate VLAN name when not defined on equipment
        :param vlan_id:
        :return:
        """
        return "VLAN%s" % vlan_id

    def get_default_vlan_description(self, vlan_id):
        """
        Generate VLAN description
        :param vlan_id:
        :return:
        """
        return "Discovered at %s(%s)" % (self.object.name, self.object.address)

    def get_object_vlans(self, l2domain: "L2Domain") -> List["DiscoveryVLAN"]:
        """
        Get vlans from equipment
        :return:
        """
        if self.object.object_profile.vlan_vlandb_discovery == "D":
            self.logger.info(
                "VLAN Database Discovery is disabled. Skipping database vlan discovery"
            )
            return []
        if self.object.l2domain.get_vlan_discovery_policy() == "D":
            self.logger.info("[%s] Collecting VLANs", l2domain.name)
            obj_vlans = self.get_data()
            if obj_vlans:
                return [
                    DiscoveryVLAN(
                        id=v["vlan_id"],
                        l2domain=l2domain,
                        name=v.get("name"),
                    )
                    for v in obj_vlans
                ]
            self.logger.info("No any VLAN found")
            return []
        else:
            self.logger.info(
                "[%s] VLAN discovery is disabled. Not collecting VLANs", self.object.segment.name
            )
            return []

    def get_interface_vlans(self, l2domain: "L2Domain") -> List["DiscoveryVLAN"]:
        """
        Get addresses from interface discovery artifact
        :return:
        """
        self.logger.debug("Getting interface vlans")
        if self.object.object_profile.vlan_interface_discovery == "D":
            self.logger.info(
                "VLAN Interface Discovery is disabled. Skipping interface vlan discovery"
            )
            return []
        vlans = self.get_artefact("interface_assigned_vlans")
        if not vlans:
            self.logger.info("No interface_assigned_vlans artefact, skipping interface vlans")
            return []
        return [
            DiscoveryVLAN(
                id=v,
                l2domain=l2domain,
            )
            for v in vlans
        ]

    def merge_vlans(self, vlans: List["DiscoveryVLAN"]) -> List["DiscoveryVLAN"]:
        """
        Merge object vlans with artifactory ones
        :param vlans:
        :return:
        """
        r = []
        proccessed = []
        for v in vlans:
            if v.id in proccessed:
                continue
            r.append(v)
            proccessed.append(v.id)
        return vlans

    def get_segment_vlans(self, vlans):
        """
        Group by vlans by segment
        :param vlans: List of (segment, vlan id, name, description)
        :return: segment -> vlan id -> (name, description)
        """
        segment_vlans = {}  # segment -> vlan -> (name, description)
        for segment, vlan, name, description in vlans:
            name = name or self.get_default_vlan_name(vlan)
            description = description or self.get_default_vlan_description(vlan)
            if segment in segment_vlans:
                if vlan in segment_vlans[segment]:
                    segment_vlans[segment][vlan] = (
                        # @todo: Smarter merge
                        segment_vlans[segment][vlan][0] or name,
                        segment_vlans[segment][vlan][1] or description,
                    )
                else:
                    segment_vlans[segment][vlan] = (name, description)
            else:
                segment_vlans[segment] = {vlan: (name, description)}
        return segment_vlans

    def get_vlan_cache(self, segments):
        """
        Fetch existing vlans from segment
        :param segments: List of segment instances
        :return: (segment, vlan id) -> VLAN instance
        """
        metrics["vlan_segment_fetch"] += 1
        self.logger.info(
            "Bulk fetching vlans from segments: %s", ",".join(s.name for s in segments)
        )
        return {
            (v.segment, v.vlan): v
            for v in VLAN.objects.filter(segment__in=[s.id for s in segments])
        }

    def ensure_vlans(self, vlans):
        """
        Synchronize all vlans
        :param segment_vlans:
        :param use_cache:
        :return:
        """
        # Group by segments
        segment_vlans = self.get_segment_vlans(vlans)
        # Bulk fetch VLANs from segments when necessary
        if len(vlans) >= self.FULL_VLANS_THRESHOLD:
            cache = self.get_vlan_cache(list(segment_vlans))
        else:
            cache = None
        result = []
        for segment in segment_vlans:
            result += [
                self.ensure_vlan(
                    segment,
                    vlan,
                    segment_vlans[segment][vlan][0],
                    segment_vlans[segment][vlan][1],
                    cache,
                )
                for vlan in segment_vlans[segment]
            ]
        return result

    def refresh_discovery_timestamps(self, vlans):
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

    def send_seen_events(self, vlans):
        """
        Send *seen* event to all vlans from list
        :param vlans: List of VLAN instances
        :return: None
        """
        for vlan in vlans:
            vlan.fire_event("seen")

    def get_policy(self):
        return self.object.get_vlan_discovery_policy()

    def get_data_from_script(self):
        return self.object.scripts.get_vlans()

    def get_data_from_confdb(self):
        r = [
            {"vlan_id": d["vlan"], "name": d.get("name", "VLAN %s" % d["vlan"])}
            for d in self.confdb.query(self.VLAN_QUERY)
        ]
        return IGetVlans().clean_result(r)
