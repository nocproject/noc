# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Extended MAC discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import List

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

    def process_direct_downlink(self, iface, macs):
        # type: (Interface,  List[MAC]) -> None
        """
        Direct downlink method. When:

        * Exactly one MAC address on port
        * MAC belongs to known chassis id
        * Related Managed Object has exactly one `direct uplink` port

        Then connect given port to `direct uplink` port

        :param iface: Interface instance
        :param macs: List of MACs seen on interface
        """
        if len(macs) != 1:
            self.logger.info(
                "[direct downlink][%s] Exactly one MAC address on port required. %d seen. Skipping",
                iface.name,
                len(macs),
            )
            return
        mac = macs[0]
        ro = self.get_neighbor_by_mac(mac)
        if not ro:
            self.logger.info(
                "[direct downlink][%s] No neighbor found for %s. Skipping", iface.name, mac
            )
            return
        self.logger.info(
            "[direct downlink][%s] Neighbor %s is found for %s", iface.name, ro.name, mac
        )
        ris = self.find_direct_uplinks(ro)
        if len(ris) != 1:
            self.logger.info(
                "[direct downlink][%s] Exactly one direct downlink interface required. "
                "%d found. Skipping",
                iface.name,
                len(ris),
            )
        ri = ris[0]
        self.confirm_interface_link(iface, ri)

    def process_chained_downlink(self, iface, macs):
        # type: (Interface,  List[MAC]) -> None
        pass

    @staticmethod
    def find_direct_uplinks(mo):
        # type: (ManagedObject) -> List[Interface]
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
