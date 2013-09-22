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
        port_macs = defaultdict(lambda: defaultdict(list))  # port -> vlan -> [macs]
        self.report = MACReport(self, to_save=self.to_save)
        vc_domain = VCDomain.get_for_object(self.object)
        for v in result:
            if v["type"] == "D" and v["interfaces"]:
                iface = v["interfaces"][0]
                port_macs[iface][v["vlan_id"]] += [v["mac"]]
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
        # Find suitable ports
        for port in port_macs:
            vlans = port_macs[port]
            if any(1 for vlan in vlans if len(vlans[vlan]) != 1):
                continue
            # Suitable port found, only one MAC in each vlan
            macs = [(vlan, vlans[vlan][0]) for vlan in vlans]
            self.check_port(port, macs)
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

    def check_port(self, port, macs):
        """
        Check link candidate and submit link if any
        :param local_port: Local port name
        :param macs: [(vlan, mac), ...]
        :return:
        """
        # Local interface
        iface = Interface.objects.filter(
            managed_object=self.object.id, name=port).first()
        if not iface:
            return  # Not found
        # Check interface is still unlinked
        if iface.is_linked:
            return  # Already linked
        # Find BRIDGE sub
        local_sub = iface.subinterface_set.filter(enabled_afi="BRIDGE").first()
        if not local_sub:
            return
        #
        if local_sub.untagged_vlan:
            # Untagged port
            mac = macs[0][1]
            subs = list(SubInterface.objects.filter(
                enabled_afi__in=["IPv4", "IPv6"], mac=mac))
            if len(subs) == 1:
                r_iface = subs[0].interface
                if not r_iface.is_linked:
                    self.submit_link(iface, r_iface)
        else:
            # Tagged port
            mac_vlans = defaultdict(list)
            for vlan, mac in macs:
                mac_vlans[mac] += [vlan]
            #
            r_iface = None
            for mac in mac_vlans:
                left = set(mac_vlans[mac])
                for sub in (SubInterface.objects.filter(
                    enabled_afi__in=["IPv4", "IPv6"], mac=mac)):
                    if not sub.vlan_ids:
                        break
                    vlan = sub.vlan_ids[0]
                    if vlan in left:
                        if r_iface is None:
                            r_iface = sub.interface
                        elif r_iface != sub.interface:
                            return  # Interface mismatch
                        left.remove(vlan)
                if left:
                    return  # Not all vlans found
            if r_iface and not r_iface.is_linked:
                self.submit_link(iface, r_iface)

    def submit_link(self, local_iface, remote_iface):
        self.debug("Linking %s and %s" % (local_iface, remote_iface))
        try:
            local_iface.link_ptp(remote_iface, method="mac")
        except ValueError, why:
            self.error("Linking error: %s" % why)
