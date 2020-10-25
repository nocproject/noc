# ----------------------------------------------------------------------
# InterfaceDiscovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from .base import BaseApplicator
from noc.core.text import list_to_ranges


class InterfaceDiscoveryApplicator(BaseApplicator):
    def apply(self):
        self.confdb.insert_bulk(self.iter_interfaces_discovery())
        self.confdb.insert_bulk(self.iter_subinterfaces_discovery())

    def iter_interfaces_discovery(self):
        # Get all interfaces
        confdb_ifaces = {
            ctx["ifname"]: ctx.get("description")
            for ctx in self.confdb.query(
                "Match('interfaces', ifname) or Match('interfaces', ifname, 'description', description)"
            )
        }
        for iface in Interface.objects.filter(managed_object=self.object.id):
            # Check all interfaces
            if iface.name not in confdb_ifaces:
                yield "interfaces", iface.name
            if iface.description and not confdb_ifaces.get(iface.name):
                yield "interfaces", iface.name, "description", iface.description

    UNIT_QUERY = """(
        Match("virtual-router", vr, "forwarding-instance", fi, "interfaces", ifname, "unit", unit) or
        Match("virtual-router", vr, "forwarding-instance", fi, "interfaces", ifname, "unit", unit, "description", description) or
        Match("virtual-router", vr, "forwarding-instance", fi, "interfaces", ifname, "unit", unit, "inet", "address", ipv4_addresses) or
        Match("virtual-router", vr, "forwarding-instance", fi, "interfaces", ifname, "unit", unit, "inet6", "address", ipv6_addresses) or
        Match("virtual-router", vr, "forwarding-instance", fi, "interfaces", ifname, "unit", unit, "bridge", "switchport", "tagged", tagged) or
        Match("virtual-router", vr, "forwarding-instance", fi, "interfaces", ifname, "unit", unit, "bridge", "switchport", "untagged", untagged)
    ) and Group("vr", "fi", "ifname", "unit", stack={"ipv4_addresses", "ipv6_addresses"})"""

    def iter_subinterfaces_discovery(self):
        # Get all subinterfaces
        confdb_units = {ctx["unit"]: ctx for ctx in self.confdb.query(self.UNIT_QUERY)}
        for sub in SubInterface.objects.filter(managed_object=self.object.id):
            # Check all subinterfaces
            if sub.name not in confdb_units:
                fi = sub.forwarding_instance.name if sub.forwarding_instance else "default"
                yield (
                    "virtual-router",
                    fi,
                    "forwarding-instance",
                    fi,
                    "interfaces",
                    sub.interface.name,
                    "unit",
                    sub.name,
                )
                if sub.description:
                    yield (
                        "virtual-router",
                        fi,
                        "forwarding-instance",
                        fi,
                        "interfaces",
                        sub.interface.name,
                        "unit",
                        sub.name,
                        "description",
                        sub.description,
                    )
                if sub.untagged_vlan:
                    yield (
                        "virtual-router",
                        fi,
                        "forwarding-instance",
                        fi,
                        "interfaces",
                        sub.interface.name,
                        "unit",
                        sub.name,
                        "bridge",
                        "switchport",
                        "untagged",
                        sub.untagged_vlan,
                    )
                if sub.tagged_vlans:
                    yield (
                        "virtual-router",
                        fi,
                        "forwarding-instance",
                        fi,
                        "interfaces",
                        sub.interface.name,
                        "unit",
                        sub.name,
                        "bridge",
                        "switchport",
                        "tagged",
                        list_to_ranges(sub.tagged_vlans),
                    )
                for a in sub.ipv4_addresses:
                    yield (
                        "virtual-router",
                        fi,
                        "forwarding-instance",
                        fi,
                        "interfaces",
                        sub.interface.name,
                        "unit",
                        sub.name,
                        "inet",
                        "address",
                        a,
                    )
                for a in sub.ipv6_addresses:
                    yield (
                        "virtual-router",
                        fi,
                        "forwarding-instance",
                        fi,
                        "interfaces",
                        sub.interface.name,
                        "unit",
                        sub.name,
                        "inet6",
                        "address",
                        a,
                    )
