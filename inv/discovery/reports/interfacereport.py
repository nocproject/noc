## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface discovery report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Report
from prefixreport import PrefixReport
from ipreport import IPReport
from noc.inv.models.forwardinginstance import ForwardingInstance
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.discovery.caches.vrf import vrf_cache


class InterfaceReport(Report):
    system_notification = "sa.version_inventory" # @todo: change

    def __init__(self, job, enabled=True, to_save=False):
        super(InterfaceReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.prefix_report = PrefixReport(job,
            enabled=job.prefix_discovery_enable and job.object.object_profile.enable_prefix_discovery,
            to_save=job.prefix_discovery_save)
        self.ip_report = IPReport(job,
            enabled=job.ip_discovery_enable and job.object.object_profile.enable_ip_discovery,
            to_save=job.ip_discovery_save
        )

    def submit_forwarding_instances(self, fi):
        """
        Delete hanging forwarding instances
        :param fi: generator yielding instance names
        :return:
        """
        db_fi = set(i["name"] for i in
            ForwardingInstance.objects.filter(
                managed_object=self.object.id).only("name"))
        for i in db_fi - set(fi):
            self.info("Removing forwarding instance %s" % i)
            for dfi in ForwardingInstance.objects.filter(
                managed_object=self.object.id, name=i):
                dfi.delete()

    def submit_interfaces(self, interfaces):
        """
        Delete hanging interfaces
        :param interfaces: generator yielding interfaces names
        :return:
        """
        if not self.enabled:
            return
        db_iface = set(i["name"] for i in
            Interface.objects.filter(
                managed_object=self.object.id).only("name"))
        for i in db_iface - set(interfaces):
            self.info("Removing interface %s" % i)
            di = Interface.objects.filter(
                managed_object=self.object.id, name=i).first()
            if di:
                di.delete()

    def submit_subinterfaces(self, forwarding_instance,
                             interface, subinterfaces):
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
            self.info("Removing subinterface %s" % i)
            dsi = SubInterface.objects.filter(
                managed_object=self.object.id,
                interface=interface.id,
                name=i).first()
            if dsi:
                dsi.delete()

    def submit_forwarding_instance(self, instance, type,
                                   rd=None, vr=None):
        """
        Register forwarding instance
        :param instance:
        :param type:
        :return:
        """
        if instance == "default":
            return None
        fi = ForwardingInstance.objects.filter(
            managed_object=self.object.id, name=instance).first()
        if fi:
            changes = self.update_if_changed(fi, {
                "type": type,
                "name": instance,
                "rd": rd if rd else fi.rd
            })
            self.log_changes(
                "Forwarding instance '%s' has been changed" % instance,
                changes)
        else:
            # Create forwarding instance
            self.info("Creating forwarding instance '%s' (%s)" % (
                instance, type))
            fi = ForwardingInstance(
                managed_object=self.object.id,
                name=instance,
                type=type,
                rd=rd,
                virtual_router=vr)
            fi.save()
        return fi

    def submit_interface(self, name, type,
                         mac=None, description=None,
                         aggregated_interface=None,
                         enabled_protocols=None,
                         ifindex=None
                         ):
        enabled_protocols = enabled_protocols or []
        iface = Interface.objects.filter(
            managed_object=self.object.id, name=name).first()
        if iface:
            # Interface exists
            changes = self.update_if_changed(iface, {
                "type": type,
                "mac": mac,
                "description": description,
                "aggregated_interface": aggregated_interface,
                "enabled_protocols": enabled_protocols,
                "ifindex": ifindex
            })
            self.log_changes("Interface '%s' has been changed" % name,
                changes)
        else:
            # Create interface
            self.info("Creating interface '%s'" % name)
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
        si = SubInterface.objects.filter(
            interface=interface.id, name=name).first()
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
            })
            self.log_changes(
                "Subinterface '%s' has been changed" % name,
                changes)
        else:
            self.info("Creating subinterface '%s'" % name)
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
        # Submit found addresses and prefixes
        if "IPv4" in enabled_afi or "IPv6" in enabled_afi:
            # Get VRF
            vrf = vrf_cache.get_or_create(
                self.object,
                forwarding_instance.name if forwarding_instance else "default",
                forwarding_instance.rd if forwarding_instance else "0:0")
            if vrf is None:
                self.info("Skipping unknown VRF '%s'" % vrf["name"])
            else:
                # Submit ipv4 addresses and prefixes
                if "IPv4" in enabled_afi:
                    for a in ipv4_addresses:
                        self.prefix_report.submit(vrf, a,
                            interface=si.name, description=si.description)
                        self.ip_report.submit(vrf, a.split("/")[0],
                            interface=si.name, mac=si.mac)
                # Submit ipv6 addresses and prefixes
                if "IPv6" in enabled_afi:
                    for a in ipv6_addresses:
                        self.prefix_report.submit(vrf, a,
                            interface=si.name, description=si.description)
                        self.ip_report.submit(vrf, a.split("/")[0],
                            interface=si.name, mac=si.mac)
                # Process dual-stacking
                if (len(ipv4_addresses) == len(ipv6_addresses) and
                    len(ipv4_addresses) > 0):
                    for ipv4, ipv6 in zip(ipv4_addresses, ipv6_addresses):
                        self.prefix_report.submit_dual_stack(vrf, ipv4, ipv6)
        return si

    def send(self):
        self.prefix_report.send()
        self.ip_report.send()
