## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.inv.discovery.reports.interfacereport import InterfaceReport
from noc.settings import config
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.lib.solutions import get_solution


class InterfaceDiscoveryJob(MODiscoveryJob):
    name = "interface_discovery"
    map_task = "get_interfaces"

    ignored = not config.getboolean("interface_discovery", "enabled")
    initial_submit_interval = config.getint("interface_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("interface_discovery",
        "initial_submit_concurrency")
    to_save = config.getboolean("interface_discovery", "save")  # @todo: Ignored
    # Related reports
    ip_discovery_enable = config.getboolean("ip_discovery", "enabled")
    ip_discovery_save = config.getboolean("ip_discovery", "save")
    prefix_discovery_enable = config.getboolean(
        "prefix_discovery", "enabled")
    prefix_discovery_save = config.getboolean(
            "prefix_discovery", "save")

    @classmethod
    def initialize(cls, scheduler):
        super(InterfaceDiscoveryJob, cls).initialize(scheduler)
        cls.get_interface_profile = None
        if scheduler.daemon:
            # Compile classification rules
            sol = config.get("interface_discovery", "get_interface_profile")
            if sol:
                cls.get_interface_profile = get_solution(sol)

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        self.profiles_cache = {}
        self.report = InterfaceReport(self, to_save=self.to_save)
        self.seen_interfaces = []
        # Process forwarding instances
        for fi in result:
            forwarding_instance = self.report.submit_forwarding_instance(
                instance=fi["forwarding_instance"],
                type=fi["type"],
                rd=fi.get("rd"),
                vr=fi.get("virtual_router")
            )
            # Move LAG members to the end
            # to make use of cache
            ifaces = sorted(fi["interfaces"],
                key=lambda x: ("aggregated_interface" in x and
                               bool(x["aggregated_interface"])))
            icache = {}
            for i in ifaces:
                # Get LAG
                agg = None
                if ("aggregated_interface" in i and
                    bool(i["aggregated_interface"])):
                        agg = icache.get(i["aggregated_interface"])
                        if not agg:
                            self.error(
                                "Cannot find aggregated interface '%s'. Skipping %s" % (
                                    i["aggregated_interface"], i["name"]))
                            continue
                # Submit discovered interface
                iface = self.report.submit_interface(
                    name=i["name"], type=i["type"], mac=i.get("mac"),
                    description=i.get("description"),
                    aggregated_interface=agg,
                    enabled_protocols=i.get("enabled_protocols", []),
                    ifindex=i.get("snmp_ifindex")
                )
                icache[i["name"]] = iface
                # Submit subinterfaces
                for si in i["subinterfaces"]:
                    self.report.submit_subinterface(
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
                self.report.submit_subinterfaces(
                    forwarding_instance, iface,
                    [si["name"] for si in i["subinterfaces"]])
                # Perform interface classification
                self.interface_classification(iface)
            # Delete hanging interfaces
            self.seen_interfaces += [i["name"] for i in fi["interfaces"]]
        # Delete hanging interfaces
        self.report.submit_interfaces(self.seen_interfaces)
        # Delete hanging forwarding instances
        self.report.submit_forwarding_instances(
            fi["forwarding_instance"] for fi in result)
        self.report.send()
        return True

    def interface_classification(self, iface):
        """
        Perform interface classification
        :param iface: Interface instance
        :return:
        """
        if not self.get_interface_profile or iface.profile_locked:
            return
        p_name = self.get_interface_profile(iface)
        if p_name and p_name != iface.profile.name:
            # Change profile
            p = self.profiles_cache.get(p_name)
            if p is None:
                p = InterfaceProfile.objects.filter(name=p_name).first()
                if p:
                    self.profiles_cache[p_name] = p
                else:
                    self.error(
                        "Invalid interface profile '%s' for interface '%s'" % (
                            p_name, iface.name))
            if p and p != iface.profile:
                self.info(
                    "Interface %s has been classified as '%s'" % (
                        iface.name, p_name))
                iface.profile = p
                iface.save()

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_interface_discovery": True}

    def can_run(self):
        return (super(InterfaceDiscoveryJob, self).can_run()
                and self.object.object_profile.enable_interface_discovery)

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.interface_discovery_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.interface_discovery_min_interval
