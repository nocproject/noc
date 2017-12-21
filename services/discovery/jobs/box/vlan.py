# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vlan check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.networksegment import NetworkSegment
from noc.vc.models.vlan import VLAN
from noc.core.perf import metrics


class VLANCheck(DiscoveryCheck):
    """
    VLAN discovery
    """
    name = "vlan"
    required_script = "get_vlans"
    # @todo: required_capabilities = ?
    # Fetch all segment VLANs if exceeded
    FULL_VLANS_THRESHOLD = 50

    def handler(self):
        self.logger.info("Checking VLANs")
        if not self.object.segment.profile.enable_vlan:
            self.logger.info(
                "VLAN discovery is disabled for segment '%s'. Skipping",
                self.object.segment.name
            )
            return
        # Get effective border segment
        segment = NetworkSegment.get_border_segment(self.object.segment)
        # Get list of VLANs from equipment
        object_vlans = self.get_vlans(segment)
        # Merge with artifactory ones
        collected_vlans = self.merge_vlans(object_vlans)
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

    def ensure_vlan(self, segment, vlan, name, description, cache):
        """
        Refresh VLAN status in database, create when necessary
        :param segment: NetworkSegment instance
        :param vlan: VLAN id
        :param name: VLAN name
        :param description: VLAN description
        :param cache: VLAN cache dictionary
        :return:
        """
        # Get existing VLAN
        if cache:
            # Get from cache
            metrics["vlan_cached_get"] += 1
            vlan = cache.get((segment, vlan))
        else:
            # Get from database
            metrics["vlan_db_get"] += 1
            vlan = VLAN.objects.filter(segment=segment.id,
                                       vlan=vlan).first()
        # Create VLAN when necessary
        if not vlan:
            self.logger.info("[%s] Creating VLAN %s(%s)",
                             segment.name, vlan, name)
            vlan = VLAN(
                name=name,
                profile=segment.profile.default_vlan_profile,
                vlan=vlan,
                segment=segment,
                description=description
            )
            vlan.save()
            metrics["vlan_created"] += 1
        return vlan

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

    def get_vlans(self, segment):
        """
        Get vlans from equipment
        :return:
        """
        if self.object.segment.profile.enable_vlan:
            self.logger.info("[%s] Collecting VLANs", self.object.segment.name)
            vlans = [
                # segment, vlan, name, description
                (segment, v["vlan_id"], v.get("name"), None)
                for v in self.object.scripts.get_vlans()
            ]
            if not vlans:
                self.logger.info("No any VLAN found")
            return vlans
        else:
            self.logger.info(
                "[%s] VLAN discovery is disabled. Not collecting VLANs",
                self.object.segment.name
            )
            return []

    def merge_vlans(self, vlans):
        """
        Merge object vlans with artifactory ones
        :param vlans:
        :return:
        """
        # @todo: Collect artifact
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
                        segment_vlans[segment][vlan][1] or description
                    )
                else:
                    segment_vlans[segment][vlan] = (name, description)
            else:
                segment_vlans[segment] = {
                    vlan: (name, description)
                }
        return segment_vlans

    def get_vlan_cache(self, segments):
        """
        Fetch existing vlans from segment
        :param segments: List of segment instances
        :return: (segment, vlan id) -> VLAN instance
        """
        metrics["vlan_segment_fetch"] += 1
        self.logger.info("Bulk fetching vlans from segments: %s",
                         ",".join(s.name for s in segments))
        return dict(
            ((v.segment, v.vlan), v)
            for v in VLAN.objects.filter(
                segment__in=[s.id for s in segments]
            )
        )

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
                    cache
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
