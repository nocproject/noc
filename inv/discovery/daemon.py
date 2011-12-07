## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import logging
import random
import time
import datetime
## Django modules
from django.db import reset_queries
## NOC modules
from noc.lib.daemon import Daemon
from noc.sa.models import ManagedObject, profile_registry, ReduceTask
from noc.inv.models import Interface, ForwardingInstance, SubInterface,\
                           DiscoveryStatusInterface
from noc.lib.debug import error_report


class DiscoveryDaemon(Daemon):
    daemon_name = "noc-discovery"

    def __init__(self, *args, **kwargs):
        super(DiscoveryDaemon, self).__init__(*args, **kwargs)
        self.pmap_interfaces = [p for p in profile_registry.classes
                    if "get_interfaces" in profile_registry.classes[p].scripts]

    def load_config(self):
        super(DiscoveryDaemon, self).load_config()
        self.enable_interface_discovery = self.config.getboolean(
                                                        "interface_discovery",
                                                        "enabled")
        self.i_reschedule_interval = self.config.getint("interface_discovery",
                                                        "reschedule_interval")
        self.i_concurrency = self.config.getint("interface_discovery",
                                                "concurrency")
        self.i_success_retry = self.config.getint("interface_discovery",
                                                  "success_retry")
        self.i_failed_retry = self.config.getint("interface_discovery",
                                                 "failed_retry")
        self.i_success_retry_range = (int(self.i_success_retry * 0.9),
                                      int(self.i_success_retry * 1.1))
        self.i_failed_retry_range = (int(self.i_failed_retry * 0.9),
                                     int(self.i_failed_retry * 1.1))


    def run(self):
        last_i_check = 0
        interface_discovery_task = None
        while True:
            reset_queries()
            now = time.time()
            if self.enable_interface_discovery:
                # Interface discovery
                if now - last_i_check >= self.i_reschedule_interval:
                    # Schedule new objects to discover
                    self.schedule_interface_discovery()
                    last_i_check = time.time()
                if interface_discovery_task is None:
                    # Start new interface discovery round
                    interface_discovery_task = self.run_interface_discovery()
                else:
                    # Check discovery is completed
                    try:
                        r = interface_discovery_task.get_result(block=False)
                    except ReduceTask.NotReady:
                        r = None
                    if r:
                        self.process_interface_discovery(r)
                        interface_discovery_task = None
            time.sleep(1)

    def o_info(self, managed_object, msg):
        logging.info("[%s] %s" % (managed_object.name, msg))

    def update_if_changed(self, obj, values):
        """
        Update fields if changed.
        :param obj: Document instance
        :type obj: Document
        :param values: New values
        :type values: dict
        :returns: List of changed (key, value)
        :rtype: list
        """
        changes = []
        for k, v in values.items():
            vv = getattr(obj, k)
            if v != vv:
                setattr(obj, k, v)
                changes += [(k, v)]
        if changes:
            obj.save()
        return changes

    def log_changes(self, o, msg, changes):
        """
        Log changes
        :param o: managed object
        :type o: ManagedObject
        :param msg: Message
        :type msg: str
        """
        if changes:
            self.o_info(o, "%s: %s" % (msg, ", ".join(["%s = %s" % (k, v)
                                                       for k, v in changes])))

    def run_interface_discovery(self):
        """
        Run interface discovery round
        :rtype: ReduceTask
        """
        ido = [s.managed_object
               for s in DiscoveryStatusInterface.objects\
                    .filter(next_check__lte=datetime.datetime.now())\
                    .only("managed_object").limit(self.i_concurrency)]
        if ido:
            logging.info("Running interface discovery for %s" % ", ".join([o.name for o in ido]))
            task = ReduceTask.create_task(ido,
                    interface_discovery_reduce, {},
                    "get_interfaces", {})
            return task
        else:
            return None

    def process_interface_discovery(self, r):
        """
        Process interface discovery results
        """
        for o, status, result in r:
            if status == "C":
                try:
                    self.import_interfaces(o, result)
                except:
                    error_report()
                DiscoveryStatusInterface.reschedule(o,
                    random.randint(*self.i_success_retry_range), True)
            else:
                self.o_info(o, "get_interfaces failed: %s" % result)
                DiscoveryStatusInterface.reschedule(o,
                    random.randint(*self.i_failed_retry_range), False)

    def import_interfaces(self, o, interfaces):
        si_count = 0
        found_interfaces = set()
        for fi in interfaces:
            ## Process forwarding instance
            if fi["forwarding_instance"] == "default":
                forwarding_instance = None
            else:
                forwarding_instance = ForwardingInstance.objects.filter(
                    managed_object=o.id,
                    name=fi["forwarding_instance"]).first()
                if forwarding_instance:
                    changes = self.update_if_changed(forwarding_instance, {
                        "type": fi["type"],
                        "forwarding_instance": fi["forwarding_instance"]
                    })
                    self.log_changes(o, "Forwarding instance '%s' has been changed" % forwarding_instance,
                                     changes)
                else:
                    # Create forwarding instance
                    self.o_info(o, "Creating forwarding instance '%s'" % fi["forwarding_instance"])
                    forwarding_instance = ForwardingInstance(
                        managed_object=o.id,
                        forwarding_instance=fi["forwarding_instance"],
                        type=fi["type"],
                        virtual_router=fi["virtual_router"])
                    forwarding_instance.save()
            ## Process physical interfaces
            icache = {}  # name -> interface instance
            ifaces = sorted(fi["interfaces"],
                            key=lambda x: ("aggregated_interface" in x
                                            and bool(x["aggregated_interface"])))
            for i in ifaces:
                iface = Interface.objects.filter(managed_object=o.id,
                    name=i["name"]).first()
                if ("aggregated_interface" in i and
                    bool(i["aggregated_interface"])):
                    agg = icache[i["aggregated_interface"]]
                else:
                    agg = None
                if iface:
                    # Interface exists
                    changes = self.update_if_changed(iface, {
                        "type": i["type"],
                        "mac": i.get("mac"),
                        "aggregated_interface": agg,
                        "is_lacp": "is_lacp" in i and i["is_lacp"]
                    })
                    self.log_changes(o, "Interface '%s' has been changed" % i["name"],
                                     changes)
                else:
                    # Create interface
                    self.o_info(o, "Creating interface '%s'" % i["name"])
                    iface = Interface(
                        managed_object=o.id,
                        name=i["name"],
                        type=i["type"],
                        mac=i.get("mac"),
                        aggregated_interface=agg,
                        is_lacp="is_lacp" in i and i["is_lacp"]
                    )
                    iface.save()
                icache[i["name"]] = iface
                found_interfaces.add(i["name"])
                # Install subinterfaces
                for si in i["subinterfaces"]:
                    s_iface = SubInterface.objects.filter(interface=iface.id,
                            name=si["name"]).first()
                    if s_iface:
                        changes = self.update_if_changed(s_iface, {
                            "description": si.get("description"),
                            "mac": si.get("mac"),
                            "vlan_ids": si.get("vlan_ids", []),
                            "is_ipv4": si.get("is_ipv4", False),
                            "is_ipv6": si.get("is_ipv6", False),
                            "is_mpls": si.get("is_mpls", False),
                            "is_bridge": si.get("is_bridge", False),
                            "ipv4_addresses": si.get("ipv4_addresses", []),
                            "ipv6_addresses": si.get("ipv6_addresses", []),
                            "iso_addresses": si.get("iso_addresses", []),
                            "is_isis": si.get("is_isis", False),
                            "is_ospf": si.get("is_ospf", False),
                            "is_rsvp": si.get("is_rsvp", False),
                            "is_ldp": si.get("is_ldp", False),
                            "is_rip": si.get("is_rip", False),
                            "is_bgp": si.get("is_bgp", False),
                            "is_eigrp": si.get("is_eigrp", False),
                            "untagged_vlan": si.get("untagged_vlan"),
                            "tagged_vlans": si.get("tagged_vlans", []),
                            # ip_unnumbered_subinterface
                            "ifindex": si.get("snmp_ifindex")
                        })
                        self.log_changes(o, "Subinterface '%s' has been changed" % si["name"],
                                         changes)
                    else:
                        self.o_info(o, "Creating subinterface '%s'" % si["name"])
                        s_iface = SubInterface(
                            interface=iface.id,
                            name=si["name"],
                            description=si.get("description"),
                            mac=si.get("mac"),
                            vlan_ids=si.get("vlan_ids", []),
                            is_ipv4=si.get("is_ipv4", False),
                            is_ipv6=si.get("is_ipv6", False),
                            is_mpls=si.get("is_mpls", False),
                            is_bridge=si.get("is_bridge", False),
                            ipv4_addresses=si.get("ipv4_addresses", []),
                            ipv6_addresses=si.get("ipv6_addresses", []),
                            iso_addresses=si.get("iso_addresses", []),
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
                        s_iface.save()
                    si_count += 1
        # Remove hanging interfaces
        db_interfaces = set([x.name for x in
                Interface.objects.filter(managed_object=o.id).only("name")])
        for i in db_interfaces - found_interfaces:
            iface = Interface.objects.filter(managed_object=o.id, name=i).first()
            if iface:
                self.o_info(o, "Delete interface '%s'" % i.name)
                SubInterface.objects.filter(interface=iface.id).delete()
                iface.delete()
        # @todo: Remove hanging forwarding instances
        self.o_info(o, "summary: %d forwarding instances, %d interfaces, %d subinterfaces" % (
            len(interfaces), len(found_interfaces), si_count))

    def schedule_interface_discovery(self):
        logging.info("Rescheduling interface discovery")
        for o in ManagedObject.objects.filter(is_managed=True,
                                    profile_name__in=self.pmap_interfaces):
            s = DiscoveryStatusInterface.objects.filter(managed_object=o.id).first()
            if not s:
                self.o_info(o, "Initial rescheduling")
                DiscoveryStatusInterface.reschedule(o,
                    random.randint(0, self.config.getint("interface_discovery",
                                                         "failed_retry")))


def interface_discovery_reduce(task):
    return [(t.managed_object, t.status, t.script_result)
            for t in task.maptask_set.all()]
