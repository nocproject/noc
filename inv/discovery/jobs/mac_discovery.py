## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MAC Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from base import MODiscoveryJob
from noc.inv.discovery.reports.macreport import MACReport
from noc.vc.models.vcdomain import VCDomain
from noc.settings import config
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface


class MACDiscoveryJob(MODiscoveryJob):
    name = "mac_discovery"
    map_task = "get_mac_address_table"

    ignored = not config.getboolean("mac_discovery", "enabled")
    initial_submit_interval = config.getint("mac_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("mac_discovery",
        "initial_submit_concurrency")
    to_save = config.getboolean("mac_discovery", "save")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        seen = {}  # MAC -> vlan
        dups = set()
        # Detect SVI addresses seen in multiple vlans
        for v in result:
            if v["type"] == "D":
                mac = v["mac"]
                vlan = v["vlan_id"]
                if mac in seen and seen[mac] != vlan:
                    # Duplicated
                    dups.add(mac)
                else:
                    seen[mac] = vlan
        # Fill report
        port_macs = defaultdict(set)  # interface -> set(..(vlan, mac) ..)
        self.report = MACReport(self, to_save=self.to_save)
        vc_domain = VCDomain.get_for_object(self.object)
        for v in result:
            if v["type"] == "D" and v["interfaces"]:
                iface = v["interfaces"][0]
                port_macs[iface].add((v["vlan_id"], v["mac"]))
                if v["mac"] not in dups:
                    # Save to MAC DB
                    self.report.submit(
                        mac=v["mac"],
                        vc_domain=vc_domain,
                        vlan=v["vlan_id"],
                        managed_object=object,
                        if_name=iface
                    )
        # Submit found MACs to database
        self.report.send()
        # Discover topology
        # Find ports with only one MAC
        pmc = [(p, set(mac for vlan, mac in port_macs[p])) for p in port_macs]
        pmc = [(p, list(m)[0]) for p, m in pmc if len(m) == 1]
        # Drop duplicated MACs
        mh = defaultdict(int)
        for p, m in pmc:
            mh[m] += 1
        # Check all unique MACs
        for port, mac in pmc:
            if mh[mac] == 1:
                self.check_port(object, port, mac,
                    [vlan for vlan, mac in port_macs[port]])
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_mac_discovery": True}

    @classmethod
    def can_submit(cls, object):
        """
        Check object has bridge interfaces
        :param cls:
        :param object:
        :return:
        """
        return object.is_managed and bool(
            SubInterface.objects.filter(managed_object=object.id,
                enabled_afi="BRIDGE").first())

    def can_run(self):
        if not super(MACDiscoveryJob, self).can_run():
            return False
        if not self.object.object_profile.enable_mac_discovery:
            return False
        # Check object has bridge interfaces
        for si in SubInterface.objects.filter(
            managed_object=self.object.id,
            enabled_afi="BRIDGE"):
            try:
                iface = si.interface
            except Exception:
                continue  # Dereference failed
            #if iface.profile.mac_discovery:
            #    return True
            return True
        # No suitable interfaces
        return False

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.mac_discovery_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.mac_discovery_min_interval

    def check_port(self, object, port, mac, vlans):
        """
        :param object: Managed Object
        :param port: Interface Name
        :param mac: MAC address
        :param vlans: List of VLANs
        :return:
        """
        # Local interface
        iface = Interface.objects.filter(
            managed_object=object.id, name=port).first()
        if not iface:
            return  # Not found
        # Check interface is still unlinked
        if iface.is_linked:
            return  # Already linked
        # Try to find remote interface by MAC
        interfaces = list(Interface.objects.filter(mac=mac))
        if len(interfaces) != 1:
            return  # No strict match
        remote_iface = interfaces[0]
        if remote_iface.is_linked:
            return  # Remote interface is already linked
        remote_subs = list(remote_iface.subinterface_set.filter(
            enabled_afi__in=["IPv4", "IPv6"], mac=mac))
        if not remote_subs:
            return  # Cannot find remote sub by MAC
        local_sub = iface.subinterface_set.filter(enabled_afi="BRIDGE").first()
        if not local_sub:
            return  # Something goes wrong
        if not local_sub.tagged_vlans:
            if len(remote_subs) == 1:
                # Access port to L3 interface
                self.submit_link(iface, remote_iface)
        else:
            # Trunk to L3 subinterfaces
            remote_vlans = set()
            for rs in remote_subs:
                if len(rs.vlan_ids) != 1:
                    return  # No Q-in-Q support yet
                v = rs.vlan_ids[0]
                remote_vlans.add(v)
            diff = set(vlans) - remote_vlans
            native_vlan = local_sub.untagged_vlan if local_sub.untagged_vlan else 1
            if diff and diff != set([native_vlan]):
                return  # Cannot find vlan on remote interface
            # All prerequisites are met
            self.submit_link(iface, remote_iface)

    def submit_link(self, local_iface, remote_iface):
        self.debug("Linking %s and %s" % (local_iface, remote_iface))
        try:
            local_iface.link_ptp(remote_iface, method="mac")
        except ValueError, why:
            self.error("Linking error: %s" % why)
