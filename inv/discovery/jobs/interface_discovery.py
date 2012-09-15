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
from noc.inv.models.interfaceclassificationrule import InterfaceClassificationRule
from noc.main.models import PyRule


class InterfaceDiscoveryJob(MODiscoveryJob):
    name = "interface_discovery"
    map_task = "get_interfaces"

    ignored = not config.getboolean("interface_discovery", "enabled")
    initial_submit_interval = config.getint("interface_discovery",
        "initial_submit_interval")
    success_retry = config.getint("interface_discovery", "success_retry")
    failed_retry = config.getint("interface_discovery", "failed_retry")
    to_save = config.getboolean("interface_discovery", "save")  # @todo: Ignored
    # Related reports
    ip_discovery_enable = config.getboolean("ip_discovery", "enabled")
    ip_discovery_save = config.getboolean("ip_discovery", "save")
    prefix_discovery_enable = config.getboolean(
        "prefix_discovery","enabled")
    prefix_discovery_save = config.getboolean(
            "prefix_discovery","save")

    @classmethod
    def initialize(cls, scheduler):
        super(InterfaceDiscoveryJob, cls).initialize(scheduler)
        # Compile classification rules
        cls.compile_classification_rules(scheduler)

    @classmethod
    def compile_classification_rules(cls, scheduler):
        """
        Compile interface classification rules
        :param scheduler:
        :return:
        """
        cls.classification_pyrule = None
        if not cls.ignored:
            p = config.get("interface_discovery",
                "classification_pyrule")
            if p:
                # Use pyRule
                r = list(PyRule.objects.filter(name=p,
                        interface="IInterfaceClassification"))
                if r:
                    scheduler.info("Enabling interface classification pyRule '%s'" % p)
                    cls.classification_pyrule = r[0]
                else:
                    scheduler.error("Interface classification pyRule '%s' is not found. Ignoring" % p)
            elif InterfaceClassificationRule.objects.filter(is_active=True).count():
                # Load rules
                scheduler.info("Compiling interface classification rules:\n"
                               "-----[CODE]-----\n%s\n-----[END]-----" %\
                               InterfaceClassificationRule.get_classificator_code())
                cls.classification_pyrule = InterfaceClassificationRule.get_classificator()

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
                    is_lacp=i.get("is_lacp", False),
                    enabled_protocols=i.get("enabled_protocols", [])
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
                        is_ipv4=si.get("is_ipv4", False),
                        is_ipv6=si.get("is_ipv6", False),
                        is_mpls=si.get("is_mpls", False),
                        is_bridge=si.get("is_bridge", False),
                        enabled_afi=si.get("enabled_afi", []),
                        ipv4_addresses=si.get("ipv4_addresses", []),
                        ipv6_addresses=si.get("ipv6_addresses", []),
                        iso_addresses=si.get("iso_addresses", []),
                        enabled_protocols=si.get("enabled_protocols", []),
                        is_isis=si.get("is_isis", False),
                        is_ospf=si.get("is_ospf", False),
                        is_rsvp=si.get("is_rsvp", False),
                        is_ldp=si.get("is_ldp", False),
                        is_rip=si.get("is_rip", False),
                        is_bgp=si.get("is_bgp", False),
                        is_eigrp=si.get("is_eigrp", False),
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
        if not self.classification_pyrule or iface.profile_locked:
            return
        p_name = self.classification_pyrule(interface=iface)
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
