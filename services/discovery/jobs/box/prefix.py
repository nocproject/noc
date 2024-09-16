# ----------------------------------------------------------------------
# Prefix check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple, defaultdict

# Third-party modules
from typing import Dict, Tuple, List, DefaultDict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.core.perf import metrics
from noc.core.handler import get_handler
from noc.core.ip import IP


DiscoveredPrefix = namedtuple(
    "DiscoveredPrefix",
    ["vpn_id", "prefix", "profile", "description", "source", "subinterface", "vlan", "asn"],
)

GLOBAL_VRF = "0:0"
SRC_INTERFACE = "i"
SRC_NEIGHBOR = "n"
SRC_WHOIS_ROUTE = "w"
SRC_MANUAL = "M"

PREF_VALUE = {SRC_NEIGHBOR: 0, SRC_WHOIS_ROUTE: 1, SRC_INTERFACE: 2, SRC_MANUAL: 3}

LOCAL_SRC = {SRC_INTERFACE}


class PrefixCheck(DiscoveryCheck):
    name = "prefix"

    def handler(self):
        self.propagated_prefixes = set()
        prefixes = self.get_prefixes()
        self.sync_prefixes(prefixes)

    def get_prefixes(self) -> Dict[Tuple[str, str], DiscoveredPrefix]:
        """
        Discover prefixes
        :return: dict of (vpn_id, prefix) => DiscoveredPrefix
        """
        # vpn_id, prefix => DiscoveredPrefix
        prefixes: Dict[Tuple[str, str], DiscoveredPrefix] = {}
        # Apply interface prefixes
        if self.object.object_profile.enable_box_discovery_prefix_interface:
            prefixes = self.apply_prefixes(prefixes, self.get_interface_prefixes())
        return prefixes

    def sync_prefixes(self, prefixes: Dict[Tuple[str, str], DiscoveredPrefix]):
        """
        Apply prefixes to database
        :param prefixes:
        :return:
        """
        # vpn_id -> [prefix, ]
        vrf_prefixes: DefaultDict[str, List[str]] = defaultdict(list)
        for vpn_id, p in prefixes:
            vrf_prefixes[vpn_id] += [p]
        # build vpn_id -> VRF mapping
        self.logger.debug("Building VRF map")
        vrfs = {}
        for vpn_id in vrf_prefixes:
            vrf = VRF.get_by_vpn_id(vpn_id)
            if vrf:
                vrfs[vpn_id] = vrf
        missed_vpn_id = set(vrf_prefixes) - set(vrfs)
        if missed_vpn_id:
            self.logger.info(
                "RD missed in VRF database and to be ignored: %s", ", ".join(missed_vpn_id)
            )
        #
        self.logger.debug("Getting prefixes to synchronize")
        for vpn_id in vrfs:
            vrf = vrfs[vpn_id]
            seen = set()
            for p in Prefix.objects.filter(vrf=vrf, prefix__in=vrf_prefixes[vpn_id]):
                norm_prefix = IP.expand(p.prefix)
                # Confirmed prefix, apply changes and touch
                prefix = prefixes[vpn_id, norm_prefix]
                self.apply_prefix_changes(p, prefix)
                seen.add(norm_prefix)
            for p in set(vrf_prefixes[vpn_id]) - seen:
                # New prefix, create
                self.create_prefix(prefixes[vpn_id, p])

    @staticmethod
    def apply_prefixes(
        prefixes: Dict[Tuple[str, str], DiscoveredPrefix],
        discovered_prefixes: List[DiscoveredPrefix],
    ):
        """
        Apply list of discovered prefixes to prefix dict
        :param prefixes: dict of (vpn_id, prefix) => DiscoveredPrefix
        :param discovered_prefixes: List of [DiscoveredPrefix]
        :returns: Resulted prefixes
        """
        for prefix in discovered_prefixes:
            norm_prefix = IP.expand(prefix.prefix)
            old = prefixes.get((prefix.vpn_id, norm_prefix))
            if old:
                if PrefixCheck.is_preferred(old.source, prefix.source):
                    # New prefix is preferable, replace
                    prefixes[prefix.vpn_id, norm_prefix] = prefix
            else:
                # Not seen yet
                prefixes[prefix.vpn_id, norm_prefix] = prefix
        return prefixes

    def is_enabled(self):
        enabled = super().is_enabled()
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

        def get_vpn_id(vpn_id):
            if vpn_id:
                return vpn_id
            if self.object.vrf:
                return self.object.vrf.vpn_id
            return GLOBAL_VRF

        self.logger.debug("Getting interface prefixes")
        if not self.object.object_profile.prefix_profile_interface:
            self.logger.info(
                "Default interface prefix profile is not set. Skipping interface prefix discovery"
            )
            return []
        prefixes = self.get_artefact("interface_prefix")
        if not prefixes:
            self.logger.info("No interface_prefix artefact, skipping interface prefixes")
            return []
        return [
            DiscoveredPrefix(
                vpn_id=get_vpn_id(p.get("vpn_id")),
                prefix=str(IP.prefix(p["address"]).first),
                profile=self.object.object_profile.prefix_profile_interface,
                source=SRC_INTERFACE,
                description=p["description"],
                subinterface=p["subinterface"],
                vlan=get_vlan(p),
                asn=None,
            )
            for p in prefixes
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
        if self.is_ignored_prefix(prefix):
            return
        vrf = VRF.get_by_vpn_id(prefix.vpn_id)
        self.ensure_afi(vrf, prefix)
        if not self.has_prefix_permission(vrf, prefix):
            self.logger.debug(
                "Do not creating vpn_id=%s asn=%s prefix=%s: Disabled by policy",
                prefix.vpn_id,
                prefix.asn.asn if prefix.asn else None,
                prefix.prefix,
            )
            metrics["prefix_creation_denied"] += 1
            return
        p = Prefix(
            vrf=vrf,
            prefix=prefix.prefix,
            name=self.get_prefix_name(prefix),
            profile=prefix.profile,
            asn=prefix.asn,
            description=prefix.description,
            source=prefix.source,
        )
        self.logger.info(
            "Creating prefix %s (%s): name=%s profile=%s source=%s",
            p.prefix,
            p.vrf.name,
            p.name,
            p.profile.name,
            p.source,
        )
        p.save()
        self.fire_seen(p)
        metrics["prefix_created"] += 1

    def apply_prefix_changes(self, prefix, discovered_prefix):
        """
        Apply prefix changes and send signals
        :param prefix: Prefix instance
        :param discovered_prefix: DiscoveredPrefix instance
        :return:
        """
        if self.is_ignored_prefix(discovered_prefix):
            return
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
            if discovered_prefix.asn and prefix.asn != discovered_prefix.asn:
                changes += [
                    "asn: %s -> %s"
                    % (
                        prefix.asn.asn if prefix.asn else None,
                        discovered_prefix.asn.asn if discovered_prefix.asn else None,
                    )
                ]
                prefix.asn = prefix.asn
            if changes:
                self.logger.info(
                    "Changing %s (%s): %s",
                    prefix.prefix,
                    discovered_prefix.vpn_id,
                    ", ".join(changes),
                )
                prefix.save()
                metrics["prefix_updated"] += 1
        else:
            self.logger.debug(
                "Do not updating vpn_id=%s prefix=%s. Source level too low",
                discovered_prefix.prefix,
                discovered_prefix.vpn_id,
            )
            metrics["prefix_update_denied"] += 1
        self.fire_seen(prefix)

    def has_prefix_permission(self, vrf, prefix):
        """
        Check discovery has permission to manipulate prefix
        :param vrf: VRF instance
        :param prefix: DiscoveredPrefix instance
        :return:
        """
        parent = Prefix.get_parent(vrf, "6" if ":" in prefix.prefix else "4", prefix.prefix)
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
            name = prefix.profile.name_template.render_subject(**self.get_template_context(prefix))
            return self.strip(name)
        return prefix.prefix

    @staticmethod
    def strip(s):
        return s.replace("\n", "").strip()

    def get_template_context(self, prefix):
        return {"prefix": prefix, "get_handler": get_handler, "object": self.object}

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
                self.logger.info("[%s|%s] Enabling IPv6 AFI", vrf.name, vrf.vpn_id)
                vrf.afi_ipv6 = True
                vrf.save()
        elif not vrf.afi_ipv4:
            self.logger.info("[%s|%s] Enabling IPv4 AFI", vrf.name, vrf.vpn_id)
            vrf.afi_ipv4 = True
            vrf.save()

    def is_ignored_prefix(self, prefix):
        """
        Check prefix should be ignored
        :param prefix: DiscoveredPrefix instance
        :return: Boolean
        """
        return (
            prefix.prefix.startswith("127.")
            or prefix.prefix.startswith("169.254.")
            or prefix.prefix.startswith("fe80:")
        )

    def fire_seen(self, prefix):
        """
        Fire `seen` event and process `seen_propagation_policy`
        :param prefix:
        :return:
        """
        if prefix.id in self.propagated_prefixes:
            return  # Already processed
        prefix.fire_event("seen")
        self.propagated_prefixes.add(prefix.id)
        if (
            prefix.profile.seen_propagation_policy == "P"
            and prefix.parent
            and prefix.parent.profile.seen_propagation_policy != "D"
        ):
            self.fire_seen(prefix.parent)
