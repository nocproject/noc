# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Prefix check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple, defaultdict
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.core.perf import metrics
from noc.core.handler import get_handler
from noc.core.ip import IP


DiscoveredPrefix = namedtuple("DiscoveredPrefix", [
    "rd",
    "prefix",
    "profile",
    "description",
    "source",
    "subinterface",
    "vlan"
])

GLOBAL_VRF = "0:0"
SRC_INTERFACE = "i"
SRC_NEIGHBOR = "n"
SRC_MANUAL = "M"

PREF_VALUE = {
    SRC_NEIGHBOR: 0,
    SRC_INTERFACE: 1,
    SRC_MANUAL: 2
}

LOCAL_SRC = {SRC_INTERFACE}


class PrefixCheck(DiscoveryCheck):
    name = "prefix"

    def handler(self):
        prefixes = self.get_prefixes()
        self.sync_prefixes(prefixes)

    def get_prefixes(self):
        """
        Discover prefixes
        :return: dict of (rd, prefix) => DiscoveredPrefix
        """
        # rd, prefix => DiscoveredPrefix
        prefixes = {}
        # Apply interface prefixes
        if self.object.object_profile.enable_box_discovery_prefix_interface:
            prefixes = self.apply_prefixes(
                prefixes,
                self.get_interface_prefixes()
            )
        return prefixes

    def sync_prefixes(self, prefixes):
        """
        Apply prefixes to database
        :param prefixes:
        :return:
        """
        # rd -> [prefix, ]
        vrf_prefixes = defaultdict(list)
        for rd, p in prefixes:
            vrf_prefixes[rd] += [p]
        # build rd -> VRF mapping
        self.logger.debug("Building VRF map")
        vrfs = {}
        for rd in vrf_prefixes:
            vrf = VRF.get_by_rd(rd)
            if vrf:
                vrfs[rd] = vrf
        missed_rd = set(vrf_prefixes) - set(vrfs)
        if missed_rd:
            self.logger.info("RD missed in VRF database and to be ignored: %s", ", ".join(missed_rd))
        #
        self.logger.debug("Getting prefixes to synchronize")
        for rd in vrfs:
            vrf = vrfs[rd]
            seen = set()
            for p in Prefix.objects.filter(vrf=vrf, prefix__in=vrf_prefixes[rd]):
                # Confirmed prefix, apply changes and touch
                prefix = prefixes[rd, p.prefix]
                self.apply_prefix_changes(p, prefix)
                seen.add(prefix.prefix)
            for p in set(vrf_prefixes[rd]) - seen:
                # New prefix, create
                self.create_prefix(prefixes[rd, p])

    @staticmethod
    def apply_prefixes(prefixes, discovered_prefixes):
        """
        Apply list of discovered prefixes to prefix dict
        :param prefixes: dict of (rd, prefix) => DiscoveredAddress
        :param discovered_prefixes: List of [DiscoveredAddress]
        :returns: Resulted prefixes
        """
        for prefix in discovered_prefixes:
            old = prefixes.get((prefix.rd, prefix.prefix))
            if old:
                if PrefixCheck.is_preferred(old.source, prefix.source):
                    # New prefix is preferable, replace
                    prefixes[prefix.rd, prefix.prefix] = prefix
            else:
                # Not seen yet
                prefixes[prefix.rd, prefix.prefix] = prefix
        return prefixes

    def is_enabled(self):
        enabled = super(PrefixCheck, self).is_enabled()
        if not enabled:
            return False
        return self.is_enabled_for_object(self.object)

    def get_interface_prefixes(self):
        """
        Get prefixes from interface discovery artifact
        :return:
        """
        def get_vlan(data):
            vlans = data.get("vlan_ids")
            if vlans and len(vlans) == 1:
                return vlans[0]
            return None

        self.logger.debug("Getting interface prefixes")
        if not self.object.object_profile.prefix_profile_interface:
            self.logger.info("Default interface prefix profile is not set. Skipping interface prefix discovery")
            return []
        prefixes = self.get_artefact("interface_prefix")
        if not prefixes:
            self.logger.info("No interface_prefix artefact, skipping interface prefixes")
            return []
        return [
            DiscoveredPrefix(
                rd=p["rd"] or GLOBAL_VRF,
                prefix=str(IP.prefix(p["address"]).first),
                profile=self.object.object_profile.prefix_profile_interface,
                source=SRC_INTERFACE,
                description=p["description"],
                subinterface=p["subinterface"],
                vlan=get_vlan(p)
            ) for p in prefixes
        ]

    @staticmethod
    def is_preferred(old_method, new_method):
        """
        Check which method is preferable

        Preference order: interface, management, neighbor
        :param old_method:
        :param new_method:
        :return:
        """
        return PREF_VALUE[old_method] <= PREF_VALUE[new_method]

    def create_prefix(self, prefix):
        """
        Create new prefix
        :param prefix: DiscoveredPrefix instance
        :return:
        """
        vrf = VRF.get_by_rd(prefix.rd)
        self.ensure_afi(vrf, prefix)
        if not self.has_prefix_permission(vrf, prefix):
            self.logger.debug(
                "Do not creating rd=%s prefix=%s: Disabled by policy",
                prefix.rd, prefix.prefix
            )
            metrics["prefix_creation_denied"] += 1
            return
        p = Prefix(
            vrf=vrf,
            prefix=prefix.prefix,
            name=self.get_prefix_name(prefix),
            profile=prefix.profile,
            description=prefix.description,
            source=prefix.source
        )
        self.logger.info(
            "Creating prefix %s (%s): name=%s profile=%s source=%s",
            p.prefix, p.vrf.name,
            p.name, p.profile.name,
            p.source
        )
        p.save()
        p.fire_event("seen")
        metrics["prefix_created"] += 1

    def apply_prefix_changes(self, prefix, discovered_prefix):
        """
        Apply prefix changes and send signals
        :param prefix: Prefix instance
        :param discovered_prefix: DiscoveredPrefix instance
        :return:
        """
        if self.is_preferred(prefix.source, discovered_prefix.source):
            changes = []
            if prefix.source != discovered_prefix.source:
                changes += ["source: %s -> %s" % (prefix.source, discovered_prefix.source)]
                prefix.source = discovered_prefix.source
            if discovered_prefix.source in LOCAL_SRC:
                # Check name
                name = self.get_prefix_name(discovered_prefix)
                if name != prefix.name:
                    changes += ["name: %s -> %s" % (prefix.name, name)]
                    prefix.name = name
            if changes:
                self.logger.info(
                    "Changing %s (%s): %s",
                    prefix.prefix,
                    discovered_prefix.rd,
                    ", ".join(changes)
                )
                prefix.save()
                metrics["prefix_updated"] += 1
        else:
            self.logger.debug(
                "Do not updating rd=%s prefix=%s. Source level too low",
                discovered_prefix.prefix, discovered_prefix.rd
            )
            metrics["prefix_update_denied"] += 1
        prefix.fire_event("seen")

    def has_prefix_permission(self, vrf, prefix):
        """
        Check discovery has permission to manipulate prefix
        :param vrf: VRF instance
        :param prefix: DiscoveredPrefix instance
        :return:
        """
        parent = Prefix.get_parent(
            vrf,
            "6" if ":" in prefix.prefix else "4",
            prefix.prefix
        )
        if parent:
            return parent.effective_prefix_discovery == "E"
        return False

    def get_prefix_name(self, prefix):
        """
        Render address name
        :param prefix: DiscoveredAddress instance
        :return: Rendered name
        """
        if prefix.profile.name_template:
            name = prefix.profile.name_template.render_subject(
                **self.get_template_context(prefix)
            )
            return self.strip(name)
        return prefix.prefix

    @staticmethod
    def strip(s):
        return s.replace("\n", "").strip()

    def get_template_context(self, prefix):
        return {
            "prefix": prefix,
            "get_handler": get_handler,
            "object": self.object
        }

    @staticmethod
    def is_enabled_for_object(object):
        return object.object_profile.enable_box_discovery_prefix_interface

    def ensure_afi(self, vrf, prefix):
        """
        Ensure VRF has appropriate AFI enabled
        :param vrf: VRF instance
        :param prefix: DiscoveredPrefix instance
        :return:
        """
        if ":" in prefix.prefix:
            # IPv6
            if not vrf.afi_ipv6:
                self.logger.info("[%s|%s] Enabling IPv6 AFI", vrf.name, vrf.rd)
                vrf.afi_ipv6 = True
                vrf.save()
        else:
            # IPv4
            if not vrf.afi_ipv4:
                self.logger.info("[%s|%s] Enabling IPv4 AFI", vrf.name, vrf.rd)
                vrf.afi_ipv4 = True
                vrf.save()
