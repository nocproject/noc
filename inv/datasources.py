# ---------------------------------------------------------------------
# Inventory module datasources
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.datasource import DataSource
from noc.inv.models.interface import Interface
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.forwardinginstance import ForwardingInstance
from noc.sa.interfaces.base import MACAddressParameter


class InterfaceDS(DataSource):
    _name = "inv.InterfaceDS"

    def __init__(self, managed_object, interface=None, ifindex=None):
        super().__init__()
        if not interface and not ifindex:
            self._interface = None
            return
        q = {"managed_object": managed_object.id}
        if interface:
            q["name"] = managed_object.get_profile().convert_interface_name(interface)
        if ifindex:
            q["ifindex"] = int(ifindex)
        self._description = None
        self._interface = Interface.objects.filter(**q).first()
        if self._interface:
            self._description = self._interface.description
        else:
            # Try to find subinterface
            si = SubInterface.objects.filter(**q).first()
            if si:
                self._description = si.description
                self._interface = si.interface

    @property
    def name(self):
        if not self._interface:
            return None
        return self._interface.name

    @property
    def description(self):
        return self._description

    @property
    def link(self):
        if not self._interface:
            return None
        link = self._interface.link
        if link:
            return str(link.id)
        return None


class ChassisDS(DataSource):
    _name = "inv.ChassisDS"

    def __init__(self, mac=None, ipv4=None, vrf=None):
        self._object = None
        if mac:
            mac = MACAddressParameter.clean(mac)
            self._object = DiscoveryID.find_object(mac)
        if ipv4:
            if vrf is None or vrf == "default":
                if SubInterface.objects.filter(ipv4_addresses=ipv4).count() == 1:
                    self._object = (
                        SubInterface.objects.filter(ipv4_addresses=ipv4).first().managed_object
                    )
            else:
                if ForwardingInstance.objects.filter(name=vrf).count() == 1:
                    forw_inst = ForwardingInstance.objects.filter(name=vrf).first()
                    if (
                        SubInterface.objects.filter(
                            ipv4_addresses=ipv4, forwarding_instance=forw_inst
                        ).count()
                        == 1
                    ):
                        self._object = (
                            SubInterface.objects.filter(
                                ipv4_addresses=ipv4, forwarding_instance=forw_inst
                            )
                            .first()
                            .managed_object
                        )

    @property
    def object(self):
        if self._object:
            return self._object
        return None
