# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.service.rpc import RPCError
from noc.inv.models.forwardinginstance import ForwardingInstance
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceclassificationrule import InterfaceClassificationRule


class InterfaceCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "interface"
    required_script = "get_interfaces"

    def __init__(self, *args, **kwargs):
        super(InterfaceCheck, self).__init__(*args, **kwargs)
        self.get_interface_profile = InterfaceClassificationRule.get_classificator()
        self.interface_macs = set()
        self.seen_interfaces = []
        self.vrf_artefact = {}  # name -> {name:, type:, rd:}
        self.prefix_artefact = {}

    def handler(self):
        self.logger.info("Checking interfaces")
        result = self.object.scripts.get_interfaces()
        # Process forwarding instances
        for fi in result:
            # Apply forwarding instance
            forwarding_instance = self.submit_forwarding_instance(
                name=fi["forwarding_instance"],
                type=fi["type"],
                rd=fi.get("rd"),
                vr=fi.get("vr")
            )
            # Move LAG members to the end
            # for effective caching
            in_lag = lambda x: ("aggregated_interface" in x and
                                bool(x["aggregated_interface"]))
            ifaces = sorted(fi["interfaces"], key=in_lag)
            icache = {}
            for i in ifaces:
                # Get LAG
                agg = None
                if in_lag(i):
                    agg = icache.get(i["aggregated_interface"])
                    if not agg:
                        self.logger.error(
                            "Cannot find aggregated interface '%s'. "
                            "Skipping %s",
                            i["aggregated_interface"], i["name"]
                        )
                        continue
                # Submit discovered interface
                iface = self.submit_interface(
                    name=i["name"], type=i["type"], mac=i.get("mac"),
                    description=i.get("description"),
                    aggregated_interface=agg,
                    enabled_protocols=i.get("enabled_protocols", []),
                    ifindex=i.get("snmp_ifindex")
                )
                icache[i["name"]] = iface
                # Submit subinterfaces
                for si in i["subinterfaces"]:
                    self.submit_subinterface(
                        forwarding_instance=forwarding_instance,
                        interface=iface, name=si["name"],
                        description=si.get("description"),
                        mac=si.get("mac", i.get("mac")),
                        vlan_ids=si.get("vlan_ids", []),
                        enabled_afi=si.get("enabled_afi", []),
                        ipv4_addresses=si.get("ipv4_addresses", []),
                        ipv6_addresses=si.get("ipv6_addresses", []),
                        iso_addresses=si.get("iso_addresses", []),
                        vpi=si.get("vpi"),
                        vci=si.get("vci"),
                        enabled_protocols=si.get("enabled_protocols", []),
                        untagged_vlan=si.get("untagged_vlan"),
                        tagged_vlans=si.get("tagged_vlans", []),
                        # ip_unnumbered_subinterface
                        ifindex=si.get("snmp_ifindex")
                    )
                # Delete hanging subinterfaces
                self.cleanup_subinterfaces(
                    forwarding_instance, iface,
                    [si["name"] for si in i["subinterfaces"]]
                )
                # Perform interface classification
                self.interface_classification(iface)
            # Delete hanging interfaces
            self.seen_interfaces += [i["name"] for i in fi["interfaces"]]
        # Delete hanging interfaces
        self.cleanup_interfaces(self.seen_interfaces)
        # Delete hanging forwarding instances
        self.cleanup_forwarding_instances(
            fi["forwarding_instance"] for fi in result
        )
        self.resolve_ifindexes()
        self.update_caps({
            "DB | Interfaces": Interface.objects.filter(
                managed_object=self.object.id
            ).count()
        }, source="interface")
        self.set_artefact("interface_macs", self.interface_macs)
        self.set_artefact("vrf", self.vrf_artefact)

    def submit_forwarding_instance(self, name, type, rd, vr):
        if name == "default":
            return None
        forwarding_instance = ForwardingInstance.objects.filter(
            managed_object=self.object.id,
            name=name
        ).first()
        if forwarding_instance:
            changes = self.update_if_changed(
                forwarding_instance, {
                    "type": type,
                    "name": name,
                    "rd": rd
                }
            )
            self.log_changes(
                "Forwarding instance '%s' has been changed",
                changes
            )
        else:
            self.logger.info(
                "Create forwarding instance '%s' (%s)",
                name,
                type
            )
            forwarding_instance = ForwardingInstance(
                managed_object=self.object.id,
                name=name,
                type=type,
                rd=rd,
                virtual_router=vr
            )
            forwarding_instance.save()
        self.vrf_artefact[name] = {
            "name": name,
            "type": type,
            "rd": rd
        }
        return forwarding_instance

    def submit_interface(self, name, type,
                         mac=None, description=None,
                         aggregated_interface=None,
                         enabled_protocols=None,
                         ifindex=None
                         ):
        enabled_protocols = enabled_protocols or []
        iface = self.get_interface_by_name(name)
        if iface:
            # Interface exists
            changes = self.update_if_changed(iface, {
                "type": type,
                "mac": mac,
                "description": description,
                "aggregated_interface": aggregated_interface,
                "enabled_protocols": enabled_protocols,
                "ifindex": ifindex
            }, ignore_empty=["ifindex"])
            self.log_changes("Interface '%s' has been changed" % name,
                             changes)
        else:
            # Create interface
            self.logger.info("Creating interface '%s'", name)
            iface = Interface(
                managed_object=self.object.id,
                name=name,
                type=type,
                mac=mac,
                description=description,
                aggregated_interface=aggregated_interface,
                enabled_protocols=enabled_protocols,
                ifindex=ifindex
            )
            iface.save()
            self.set_interface(name, iface)
        if mac:
            self.interface_macs.add(mac)
        return iface

    def submit_subinterface(self, forwarding_instance, interface,
                            name, description=None, mac=None,
                            vlan_ids=None,
                            enabled_afi=[],
                            ipv4_addresses=[], ipv6_addresses=[],
                            iso_addresses=[], vpi=None, vci=None,
                            enabled_protocols=[],
                            untagged_vlan=None, tagged_vlans=[],
                            ifindex=None):
        mac = mac or interface.mac
        si = self.get_subinterface(interface, name)
        if si:
            changes = self.update_if_changed(si, {
                "forwarding_instance": forwarding_instance,
                "description": description,
                "mac": mac,
                "vlan_ids": vlan_ids,
                "enabled_afi": enabled_afi,
                "ipv4_addresses": ipv4_addresses,
                "ipv6_addresses": ipv6_addresses,
                "iso_addresses": iso_addresses,
                "vpi": vpi,
                "vci": vci,
                "enabled_protocols": enabled_protocols,
                "untagged_vlan": untagged_vlan,
                "tagged_vlans": tagged_vlans,
                # ip_unnumbered_subinterface
                "ifindex": ifindex
            }, ignore_empty=["ifindex"])
            self.log_changes(
                "Subinterface '%s' has been changed" % name,
                changes)
        else:
            self.logger.info("Creating subinterface '%s'", name)
            si = SubInterface(
                forwarding_instance=forwarding_instance,
                interface=interface.id,
                managed_object=self.object.id,
                name=name,
                description=description,
                mac=mac,
                vlan_ids=vlan_ids,
                enabled_afi=enabled_afi,
                ipv4_addresses=ipv4_addresses,
                ipv6_addresses=ipv6_addresses,
                iso_addresses=iso_addresses,
                vpi=None,
                vci=None,
                enabled_protocols=enabled_protocols,
                untagged_vlan=untagged_vlan,
                tagged_vlans=tagged_vlans,
                ifindex=ifindex
            )
            si.save()
        if mac:
            self.interface_macs.add(mac)
        return si

    def cleanup_forwarding_instances(self, fi):
        """
        Delete hanging forwarding instances
        :param fi: generator yielding instance names
        :return:
        """
        db_fi = set(
            i["name"] for i in
            ForwardingInstance.objects.filter(
                managed_object=self.object.id).only("name"))
        for i in db_fi - set(fi):
            self.logger.info("Removing forwarding instance %s", i)
            for dfi in ForwardingInstance.objects.filter(
                managed_object=self.object.id, name=i
            ):
                dfi.delete()

    def cleanup_interfaces(self, interfaces):
        """
        Delete hanging interfaces
        :param interfaces: generator yielding interfaces names
        :return:
        """
        db_iface = set(
            i["name"] for i in
            Interface.objects.filter(
                managed_object=self.object.id).only("name"))
        for i in db_iface - set(interfaces):
            self.logger.info("Removing interface %s", i)
            di = Interface.objects.filter(
                managed_object=self.object.id, name=i).first()
            if di:
                di.delete()

    def cleanup_subinterfaces(self, forwarding_instance, interface,
                              subinterfaces):
        """
        Delete hanging subinterfaces
        :return:
        """
        if forwarding_instance:
            fi = forwarding_instance.id
        else:
            fi = None
        qs = SubInterface.objects.filter(
            managed_object=self.object.id,
            interface=interface.id,
            forwarding_instance=fi
        )
        db_siface = set(i["name"] for i in qs.only("name"))
        for i in db_siface - set(subinterfaces):
            self.logger.info("Removing subinterface %s" % i)
            dsi = SubInterface.objects.filter(
                managed_object=self.object.id,
                interface=interface.id,
                name=i).first()
            if dsi:
                dsi.delete()

    def interface_classification(self, iface):
        """
        Perform interface classification
        :param iface: Interface instance
        :return:
        """
        if iface.profile_locked:
            return
        try:
            p_id = self.get_interface_profile(iface)
        except NotImplementedError:
            self.logger.error(
                "Uses not implemented rule"
            )
            return
        if p_id and p_id != iface.profile.id:
            # Change profile
            profile = InterfaceProfile.get_by_id(p_id)
            if not profile:
                self.logger.error(
                    "Invalid interface profile '%s' for interface '%s'. "
                    "Skipping",
                    p_id, iface.name
                )
                return
            elif profile != iface.profile:
                self.logger.info(
                    "Interface %s has been classified as '%s'",
                    iface.name, profile.name
                )
                iface.profile = profile
                iface.save()

    def resolve_ifindexes(self):
        """
        Try to resolve missed ifindexes
        """
        missed_ifindexes = [
            n[1] for n in self.if_name_cache
            if (n in self.if_name_cache and
                self.if_name_cache[n] and
                self.if_name_cache[n].ifindex is None and
                self.if_name_cache[n].type in ("physical", "aggregated")
                )
        ]
        if not missed_ifindexes:
            return
        self.logger.info(
            "Missed ifindexes for: %s",
            ", ".join(missed_ifindexes)
        )
        try:
            r = self.object.scripts.get_ifindexes()
        except RPCError:
            r = None
        if not r:
            return
        updates = {}
        for n in missed_ifindexes:
            if n in r:
                updates[n] = r[n]
        if not updates:
            return
        for n, i in six.iteritems(updates):
            iface = self.get_interface_by_name(n)
            if iface:
                self.logger.info("Set ifindex for %s: %s", n, i)
                iface.ifindex = i
                iface.save()  # Signals will be sent
