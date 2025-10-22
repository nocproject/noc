# ----------------------------------------------------------------------
# Extended MAC discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import Optional, List, Dict, Tuple

# NOC modules
from noc.core.mac import MAC
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class XMACCheck(TopologyDiscoveryCheck):
    """
    xMAC Topology discovery
    """

    name = "xmac"

    def handler(self):
        macs = self.get_artefact("mac_direct_downlink")
        if not macs:
            self.logger.info("No suitable MACs. Skipping")
            return
        for if_name in macs:
            iface = self.get_interface_by_name(if_name)
            policy = iface.get_profile().mac_discovery_policy
            if policy == "i":
                self.process_direct_downlink(iface, macs[if_name])
            elif policy == "c":
                self.process_chained_downlink(iface, macs[if_name])
            elif policy == "C":
                self.process_cloud(iface, macs[if_name])

    def process_direct_downlink(
        self, iface: Interface, macs: List[MAC], name: Optional[str] = None
    ) -> None:
        """
        Direct downlink method. When:

        * Exactly one MAC address on port
        * MAC belongs to known chassis id
        * Related Managed Object has exactly one `direct uplink` port

        Then connect given port to `direct uplink` port

        :param iface: Interface instance
        :param macs: List of MACs seen on interface
        :param name: Optional method name
        """
        name = name or "direct"
        if len(macs) != 1:
            self.logger.info(
                "[%s][%s] Exactly one MAC address on port required. %d seen. Skipping",
                name,
                iface.name,
                len(macs),
            )
            return
        mac = macs[0]
        ro = self.get_neighbor_by_mac(mac)
        if not ro:
            self.logger.info("[%s][%s] No neighbor found for %s. Skipping", name, iface.name, mac)
            return
        self.logger.info("[%s][%s] Neighbor %s is found for %s", name, iface.name, ro.name, mac)
        ris = self.find_direct_uplinks(ro)
        if len(ris) != 1:
            self.logger.info(
                "[%s][%s] Exactly one direct downlink interface required. %d found. Skipping",
                name,
                iface.name,
                len(ris),
            )
            return
        ri = ris[0]
        self.confirm_interface_link(iface, ri)

    def process_chained_downlink(
        self, iface: Interface, macs: List[MAC], name: Optional[str] = None
    ) -> None:
        """
        Chained downlink method. When:

        * Only one mac
            * Fallback to direct downlink method
        * Multiple MACs
            * All MACs belongs to known chassis ids
            * Exactly one `direct uplink` port for each object
            * All objects has different managed object levels

        Then:

        * Order objects by level in descendant order
        * Check all objects excluding last has exactly one `direct downlink` port
        * Connect all the chain by downlink-uplink

        :param iface: Interface instance
        :param macs: List of MACs seen on interface
        :param name: Optional method name
        """
        name = "chained"
        if len(macs) == 1:
            return self.process_direct_downlink(iface, macs, name)
        # Get all downlink objects
        chain = []  # type: List[ManagedObject]
        for mac in macs:
            ro = self.get_neighbor_by_mac(mac)
            if not ro:
                self.logger.info(
                    "[%s][%s] No neighbor found for %s. Cannot link.", name, iface.name, mac
                )
                return None
            self.logger.info("[%s][%s] Neighbor %s is found for %s", name, iface.name, ro.name, mac)
            chain += [ro]
        # Check all objects has different levels
        levels = {}  # type: Dict[int, ManagedObject]
        for ro in chain:
            level = ro.object_profile.level
            if level in levels:
                self.logger.info(
                    "[%s][%s] Neighbors %s and %s has same level of %d. Cannot link.",
                    name,
                    iface.name,
                    levels[level].name,
                    ro.name,
                    level,
                )
                return None
            levels[level] = ro
        # Arrange objects
        chain = sorted(chain, key=lambda x: x.object_profile.level, reverse=True)
        # Check uplinks/downlinks
        ports = self.find_direct_uplinks_downlinks(chain)
        ports[self.object] = ([], [iface])
        links = []  # type: List[Tuple[Interface, Interface]]
        for p, n in zip([self.object, *chain], chain):
            if len(ports[p][1]) != 1:
                self.logger.info(
                    "[%s][%s] Neighbor %s must have exactly one direct downlink port. %d found. Cannot link.",
                    name,
                    iface.name,
                    n.name,
                    len(ports[p][1]),
                )
                return None
            downlink = ports[p][1][0]
            if n not in ports:
                self.logger.info(
                    "[%s][%s] Neighbor %s has no direct uplink ports. Cannot link.",
                    name,
                    iface.name,
                    n.name,
                )
                return None
            if len(ports[n][0]) != 1:
                self.logger.info(
                    "[%s][%s] Neighbor %s must have exactly one direct uplink port. %d found. Cannot link.",
                    name,
                    iface.name,
                    n.name,
                    len(ports[n][0]),
                )
                return None
            uplink = ports[n][0][0]
            links += [(downlink, uplink)]
        # Link all ports
        for link in links:
            self.confirm_interface_link(*link)

    def process_cloud(self, iface: Interface, macs: List[MAC], name: Optional[str] = None) -> None:
        """
        Cloud downlink methods. When:

        * All MACs belongs to known chassis ids
        * Exactly one `direct uplink` port for each object

        Then connect all of them to cloud

        :param iface: Interface instance
        :param macs: List of MACs seen on interface
        :param name: Optional method name
        """
        name = name or "cloud"
        # Get all downlink objects
        cloud = []  # type: List[ManagedObject]
        for mac in macs:
            ro = self.get_neighbor_by_mac(mac)
            if not ro:
                self.logger.info(
                    "[%s][%s] No neighbor found for %s. Skipping.", name, iface.name, mac
                )
                continue
            self.logger.info("[%s][%s] Neighbor %s is found for %s", name, iface.name, ro.name, mac)
            if ro.object_profile.level > self.object.object_profile.level:
                self.logger.info(
                    "[%s][%s] Neighbor's %s level is greater than of root object (%d > %d).  "
                    "Malformed cloud. Skipping.",
                    name,
                    iface.name,
                    ro.object_profile.level,
                    ro.object_profile.level,
                    self.object.object_profile.level,
                )
                return
            cloud += [ro]
        # Get all cloud uplinks
        ports = self.find_direct_uplinks_downlinks(cloud)
        # Connect all interfaces to cloud link
        cloud_ifaces = []  # type: List[Interface]
        for ro in cloud:
            if ro in ports:
                uplinks = ports[ro][0]
            else:
                uplinks = []
            if len(uplinks) != 1:
                self.logger.info(
                    "[%s][%s] Neighbor %s must have exactly one direct uplink port. %d found. "
                    "Cannot attach to cloud. Skipping.",
                    name,
                    iface.name,
                    ro.name,
                    len(uplinks),
                )
                continue
            cloud_ifaces += [uplinks[0]]
        # Refresh cloud
        if cloud_ifaces:
            self.confirm_cloud(iface, cloud_ifaces)
        else:
            self.logger.info("[%s][%s] Empty cloud. Skipping.", name, iface.name)

    @staticmethod
    def find_direct_uplinks(mo: ManagedObject) -> List[Interface]:
        """
        Find all `direct uplinks` interfaces for given object

        :param mo: Managed Object instance
        :returns: List of Interface instances
        """
        return [
            iface
            for iface in Interface.objects.filter(managed_object=mo.id, type="physical")
            if iface.get_profile().mac_discovery_policy == "u"
        ]

    @staticmethod
    def find_direct_uplinks_downlinks(
        objects: List[ManagedObject],
    ) -> Dict[ManagedObject, Tuple[List[Interface], List[Interface]]]:
        """
        For all given objects return all direct uplink/direct downlink ports

        :param objects: List of Managed Objects
        :returns: Dict of ManagedObject -> (List of direct uplinks, List of direct downlinks)
        """
        r: Dict[ManagedObject, Tuple[List[Interface], List[Interface]]] = {}
        for iface in Interface.objects.filter(
            managed_object__in=[mo.id for mo in objects], type="physical"
        ):
            mo = iface.managed_object
            if mo not in r:
                r[mo] = ([], [])
            policy = iface.get_profile().mac_discovery_policy
            if policy == "u":
                uplinks = r[mo][0]
                uplinks += [iface]
            elif policy == "i":
                downlinks = r[mo][1]
                downlinks += [iface]
        return r
