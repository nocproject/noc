# ----------------------------------------------------------------------
# Address check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import binascii
from typing import List, Dict, Tuple
from collections import namedtuple, defaultdict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address
from noc.core.perf import metrics
from noc.core.handler import get_handler
from noc.core.validators import is_fqdn
from noc.core.ip import IP, PrefixDB


DiscoveredAddress = namedtuple(
    "DiscoveredAddress",
    ["vpn_id", "address", "profile", "description", "source", "subinterface", "mac", "fqdn"],
)

GLOBAL_VRF = "0:0"
SRC_MANAGEMENT = "m"
SRC_INTERFACE = "i"
SRC_DHCP = "d"
SRC_NEIGHBOR = "n"
SRC_MANUAL = "M"
SRC_PING = "P"

PREF_VALUE = {
    SRC_NEIGHBOR: 0,
    SRC_DHCP: 1,
    SRC_MANAGEMENT: 2,
    SRC_INTERFACE: 3,
    SRC_PING: 4,
    SRC_MANUAL: 5,
}

LOCAL_SRC = {SRC_MANAGEMENT, SRC_INTERFACE}


class AddressCheck(DiscoveryCheck):
    name = "address"
    do_detaching = True  # False for ip ping discovery job

    def handler(self):
        self.propagated_prefixes = set()
        addresses = self.get_addresses()
        self.sync_addresses(addresses)

    def get_addresses(self):
        """
        Discover addresses
        :return: dict of (vpn_id, address) => DiscoveredAddress
        """
        # vpn_id, address => DiscoveredAddress
        addresses = {}
        # Apply interface addresses
        if self.object.object_profile.enable_box_discovery_address_interface:
            addresses = self.apply_addresses(addresses, self.get_interface_addresses())
        # Apply management addresses
        if self.object.object_profile.enable_box_discovery_address_management:
            addresses = self.apply_addresses(addresses, self.get_management_addresses())
        # Apply DHCP leases
        if self.object.object_profile.enable_box_discovery_address_dhcp:
            addresses = self.apply_addresses(addresses, self.get_dhcp_addresses())
        # Apply neighbor addresses
        if self.object.object_profile.enable_box_discovery_address_neighbor:
            addresses = self.apply_addresses(addresses, self.get_neighbor_addresses())
        return addresses

    def sync_addresses(self, addresses):
        """
        Apply addresses to database
        :param addresses:
        :return:
        """
        # vpn_id -> [address, ]
        vrf_addresses = defaultdict(list)
        for vpn_id, a in addresses:
            vrf_addresses[vpn_id] += [a]
        # build vpn_id -> VRF mapping
        self.logger.debug("Building VRF map")
        vrfs = {}
        for vpn_id in vrf_addresses:
            vrf = VRF.get_by_vpn_id(vpn_id)
            if vrf:
                vrfs[vpn_id] = vrf
        missed_vpn_id = set(vrf_addresses) - set(vrfs)
        if missed_vpn_id:
            self.logger.info(
                "VPN ID are missed in VRF database and to be ignored: %s", ", ".join(missed_vpn_id)
            )
        #
        self.logger.debug("Getting addresses to synchronize")
        for vpn_id in vrfs:
            vrf = vrfs[vpn_id]
            seen = set()
            for a in Address.objects.filter(vrf=vrf, address__in=vrf_addresses[vpn_id]):
                norm_address = IP.expand(a.address)
                # Confirmed address, apply changes and touch
                address = addresses[vpn_id, norm_address]
                self.apply_address_changes(a, address)
                seen.add(norm_address)
            for a in set(vrf_addresses[vpn_id]) - seen:
                # New address, create
                self.create_address(addresses[vpn_id, a])
        # Detaching hanging addresses
        self.logger.debug("Checking for hanging addresses")
        if not self.do_detaching:
            return
        for a in Address.objects.filter(managed_object=self.object):
            norm_address = IP.expand(a.address)
            address = addresses.get((a.vrf.vpn_id, norm_address))
            if not address or address.source not in LOCAL_SRC:
                self.logger.info("Detaching %s:%s", a.vrf.name, a.address)
                a.managed_object = None
                a.save()

    @staticmethod
    def apply_addresses(
        addresses: Dict[Tuple[str, IP], DiscoveredAddress],
        discovered_addresses: List[DiscoveredAddress],
    ) -> Dict[Tuple[str, IP], DiscoveredAddress]:
        """
        Apply list of discovered addresses to addresses dict
        :param addresses: dict of (vpn_id, address) => DiscoveredAddress
        :param discovered_addresses: List of [DiscoveredAddress]
        :returns: Resulted addresses
        """
        for address in discovered_addresses:
            norm_address = IP.expand(address.address)
            old = addresses.get((address.vpn_id, norm_address))
            if old:
                if AddressCheck.is_preferred(old.source, address.source):
                    # New address is preferable, replace
                    addresses[address.vpn_id, norm_address] = address
            else:
                # Not seen yet
                addresses[address.vpn_id, norm_address] = address
        return addresses

    def is_enabled(self):
        enabled = super().is_enabled()
        if not enabled:
            return False
        return self.is_enabled_for_object(self.object)

    def get_interface_addresses(self) -> List[DiscoveredAddress]:
        """
        Get addresses from interface discovery artifact
        :return:
        """

        def get_vpn_id(vpn_id):
            if vpn_id:
                return vpn_id
            if self.object.vrf:
                return self.object.vrf.vpn_id
            return GLOBAL_VRF

        self.logger.debug("Getting interface addresses")
        if not self.object.object_profile.address_profile_interface:
            self.logger.info(
                "Default interface address profile is not set. Skipping interface address discovery"
            )
            return []
        addresses = self.get_artefact("interface_prefix")
        if not addresses:
            self.logger.info("No interface_prefix artefact, skipping interface addresses")
            return []
        return [
            DiscoveredAddress(
                vpn_id=get_vpn_id(a.get("vpn_id")),
                address=a["address"].rsplit("/", 1)[0],
                profile=self.object.object_profile.address_profile_interface,
                source=SRC_INTERFACE,
                description=a["description"],
                subinterface=a["subinterface"],
                mac=a["mac"],
                fqdn=None,
            )
            for a in addresses
        ]

    def get_management_addresses(self) -> List[DiscoveredAddress]:
        """
        Get addresses from ManagedObject management
        :return:
        """
        if not self.object.object_profile.address_profile_management:
            self.logger.info(
                "Default management address profile is not set. Skipping interface address discovery"
            )
            return []
        self.logger.debug("Getting management addresses")
        addresses = []
        if self.object.address:
            addresses = [
                DiscoveredAddress(
                    vpn_id=self.object.vrf.vpn_id if self.object.vrf else GLOBAL_VRF,
                    address=self.object.address,
                    profile=self.object.object_profile.address_profile_management,
                    source=SRC_MANAGEMENT,
                    description="Management address",
                    subinterface=None,
                    mac=None,
                    fqdn=self.object.get_full_fqdn(),
                )
            ]
        return addresses

    def get_dhcp_addresses(self) -> List["DiscoveredAddress"]:
        """
        Return addresses from DHCP leases
        :return:
        """

        def get_vpn_id(ip):
            try:
                return vpn_db[IP.prefix(ip)]
            except KeyError:
                pass
            if self.object.vrf:
                return self.object.vrf.vpn_id
            return GLOBAL_VRF

        if not self.object.object_profile.address_profile_dhcp:
            self.logger.info(
                "Default DHCP address profile is not set. Skipping DHCP address discovery"
            )
            return []
        # @todo: Check DHCP server capability
        if "get_dhcp_binding" not in self.object.scripts:
            self.logger.info("No get_dhcp_binding script, skipping neighbor discovery")
            return []
        # Build network -> vpn mappings
        addresses = self.get_artefact("interface_prefix")
        if not addresses:
            self.logger.info("No interface_prefix artefact, skipping interface addresses")
            return []
        vpn_db = PrefixDB()
        for a in addresses:
            vpn_db[IP.prefix(a["address"]).first] = a["vpn_id"]
        #
        self.logger.debug("Getting DHCP addresses")
        leases = self.object.scripts.get_dhcp_binding()
        r = [
            DiscoveredAddress(
                vpn_id=get_vpn_id(a["ip"]),
                address=a["ip"],
                profile=self.object.object_profile.address_profile_dhcp,
                source=SRC_DHCP,
                description=None,
                subinterface=None,
                mac=a.get("mac"),
                fqdn=None,
            )
            for a in leases
        ]
        return r

    def get_neighbor_addresses(self) -> List[DiscoveredAddress]:
        """Return addresses from ARP/IPv6 ND"""

        def get_vpn_id(vpn_id):
            if vpn_id:
                return vpn_id
            if self.object.vrf:
                return self.object.vrf.vpn_id
            return GLOBAL_VRF

        if not self.object.object_profile.address_profile_neighbor:
            self.logger.info(
                "Default neighbor address profile is not set. Skipping neighbor address discovery"
            )
            return []
        if "get_ip_discovery" not in self.object.scripts:
            self.logger.info("No get_ip_discovery script, skipping neighbor discovery")
            return []
        self.logger.debug("Getting neighbor addresses")
        neighbors = self.object.scripts.get_ip_discovery()
        r = []
        for vpn in neighbors:
            for a in vpn["addresses"]:
                r += [
                    DiscoveredAddress(
                        vpn_id=get_vpn_id(vpn.get("vpn_id")),
                        address=a["ip"],
                        profile=self.object.object_profile.address_profile_neighbor,
                        source=SRC_NEIGHBOR,
                        description=None,
                        subinterface=None,
                        mac=a.get("mac"),
                        fqdn=None,
                    )
                ]
        return r

    @staticmethod
    def is_preferred(old_method: str, new_method: str) -> bool:
        """
        Check which method is preferable

        Preference order: interface, management, neighbor
        :param old_method:
        :param new_method:
        :return:
        """
        return PREF_VALUE[old_method] <= PREF_VALUE[new_method]

    def create_address(self, address: DiscoveredAddress):
        """
        Create new address
        :param address: DiscoveredAddress instance
        :return:
        """
        if self.is_ignored_address(address):
            return
        vrf = VRF.get_by_vpn_id(address.vpn_id)
        self.ensure_afi(vrf, address)
        if not self.has_address_permission(vrf, address):
            self.logger.debug(
                "Do not creating vpn_id=%s address=%s: Disabled by policy",
                address.vpn_id,
                address.address,
            )
            metrics["address_creation_denied"] += 1
            return
        a = Address(
            vrf=vrf,
            address=address.address,
            name=self.get_address_name(address),
            fqdn=address.fqdn,
            profile=address.profile,
            description=address.description,
            source=address.source,
            mac=address.mac,
        )
        if address.source in LOCAL_SRC:
            a.managed_object = self.object
            a.subinterface = address.subinterface
        self.logger.info(
            "Creating address %s (%s): name=%s fqdn=%s mac=%s profile=%s source=%s",
            a.address,
            a.vrf.name,
            a.name,
            a.fqdn,
            a.mac,
            a.profile.name,
            a.source,
        )
        a.save()
        self.fire_seen(a)
        metrics["address_created"] += 1

    def apply_address_changes(self, address: Address, discovered_address: DiscoveredAddress):
        """
        Apply address changes and send signals
        :param address: Address instance
        :param discovered_address: DiscoveredAddress instance
        :return:
        """
        if self.is_ignored_address(discovered_address):
            return
        if self.is_preferred(address.source, discovered_address.source):
            changes = []
            if address.source != discovered_address.source:
                changes += ["source: %s -> %s" % (address.source, discovered_address.source)]
                address.source = discovered_address.source
            if discovered_address.source in LOCAL_SRC:
                # Check name
                name = self.get_address_name(discovered_address)
                if name != address.name:
                    changes += ["name: %s -> %s" % (address.name, name)]
                    address.name = name
                # Check fqdn
                if discovered_address.fqdn != address.fqdn and discovered_address.fqdn:
                    changes += ["fqdn: %s -> %s" % (address.fqdn, discovered_address.fqdn)]
                    address.fqdn = discovered_address.fqdn
                # @todo: Change profile
                # Change managed object
                if discovered_address.source in LOCAL_SRC and (
                    not address.managed_object or address.managed_object.id != self.object.id
                ):
                    changes += ["object: %s -> %s" % (address.managed_object, self.object)]
                    address.managed_object = self.object
                # Change subinterface
                if (
                    discovered_address.source == SRC_INTERFACE
                    and address.subinterface != discovered_address.subinterface
                ):
                    changes += [
                        "subinterface: %s -> %s"
                        % (address.subinterface, discovered_address.subinterface)
                    ]
                    address.subinterface = discovered_address.subinterface
            if discovered_address.mac and address.mac != discovered_address.mac:
                changes += ["mac: %s -> %s" % (address.mac, discovered_address.mac)]
                address.mac = discovered_address.mac
            if changes:
                self.logger.info(
                    "Changing %s (%s): %s",
                    address.address,
                    discovered_address.vpn_id,
                    ", ".join(changes),
                )
                address.save()
                metrics["address_updated"] += 1
        else:
            self.logger.debug(
                "Do not updating vpn_id=%s address=%s. Source level too low",
                discovered_address.vpn_id,
                discovered_address.address,
            )
            metrics["address_update_denied"] += 1
        self.fire_seen(address)

    def has_address_permission(self, vrf: VRF, address: DiscoveredAddress) -> bool:
        """
        Check discovery has permission to manipulate address
        :param vrf: VRF instance
        :param address: DiscoveredAddress instance
        :return:
        """
        parent = Prefix.get_parent(vrf, "6" if ":" in address.address else "4", address.address)
        if parent:
            return parent.effective_address_discovery == "E"
        return False

    def get_address_name(self, address: DiscoveredAddress):
        """
        Render address name
        :param address: DiscoveredAddress instance
        :return: Rendered name
        """
        if address.profile.name_template:
            name = address.profile.name_template.render_subject(
                **self.get_template_context(address)
            )
            return self.strip(name)
        return address.address

    def get_address_fqdn(self, address: DiscoveredAddress):
        """
        Render address name
        :param address: DiscoveredAddress instance
        :return: Rendered name or None
        """
        if address.profile.fqdn_template:
            fqdn = address.profile.fqdn_template.render_subject(
                **self.get_template_context(address)
            )
            fqdn = self.strip(fqdn)
            if is_fqdn(fqdn):
                return fqdn
            self.logger.error(
                "Address %s renders to invalid FQDN '%s'. Ignoring FQDN", address.address, fqdn
            )
        return None

    @staticmethod
    def strip(s):
        return s.replace("\n", "").strip()

    def get_template_context(self, address):
        return {"address": address, "get_handler": get_handler, "object": self.object}

    @staticmethod
    def is_enabled_for_object(o) -> bool:
        return (
            o.object_profile.enable_box_discovery_address_interface
            or o.object_profile.enable_box_discovery_address_management
            or o.object_profile.enable_box_discovery_address_dhcp
            or o.object_profile.enable_box_discovery_address_neighbor
        )

    def ensure_afi(self, vrf, address):
        """
        Ensure VRF has appropriate AFI enabled
        :param vrf: VRF instance
        :param address: DiscoveredAddress instance
        :return:
        """
        if ":" in address.address:
            # IPv6
            if not vrf.afi_ipv6:
                self.logger.info("[%s|%s] Enabling IPv6 AFI", vrf.name, vrf.vpn_id)
                vrf.afi_ipv6 = True
                vrf.save()
        else:
            # IPv4
            if not vrf.afi_ipv4:
                self.logger.info("[%s|%s] Enabling IPv4 AFI", vrf.name, vrf.vpn_id)
                vrf.afi_ipv4 = True
                vrf.save()

    def is_ignored_address(self, address: DiscoveredAddress):
        """
        Check address should be ignored
        :param address: DiscoveredAddress instance
        :return: boolean
        """
        return (
            address.mac == "FF:FF:FF:FF:FF:FF"
            or address.address.startswith("127.")
            or address.address.startswith("169.254.")
            or address.address == "::1"
            or address.address.startswith("fe80:")
        )

    def fire_seen(self, address):
        """
        Fire `seen` event and process `seen_propagation_policy`
        :param address:
        :return:
        """
        address.fire_event("seen")
        if address.profile.seen_propagation_policy == "D":
            return  # Disabled
        self.propagate_seen(address.prefix)

    def propagate_seen(self, prefix):
        """
        Propagate `seen` through prefix hierarchy
        :param prefix:
        :return:
        """
        if prefix.id in self.propagated_prefixes:
            return  # Already processed
        self.propagated_prefixes.add(prefix.id)
        if prefix.profile.seen_propagation_policy == "D":
            return  # Disabled
        # Fire seen
        prefix.fire_event("seen")
        if prefix.profile.seen_propagation_policy == "E":
            return  # Do not propagate upwards
        # Propagate upwards
        if prefix.parent and prefix.parent.profile.seen_propagation_policy != "D":
            self.propagate_seen(prefix.parent)
