## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import logging
import random
import time
import datetime
import re
## Django modules
from django.db import reset_queries
from django.template import Template, Context
## NOC modules
from noc.lib.daemon import Daemon
from noc.sa.models import ManagedObject, profile_registry, ReduceTask
from noc.inv.models import Interface, ForwardingInstance, SubInterface,\
                           DiscoveryStatusInterface, DiscoveryStatusIP
from noc.lib.debug import error_report
from noc.lib.ip import IP
from noc.ip.models import VRF, Prefix, AS, Address
from noc.lib.nosql import Q
from noc.main.models import SystemNotification, ResourceState


class DiscoveryDaemon(Daemon):
    daemon_name = "noc-discovery"

    rx_address = re.compile("[^0-9a-z\-]+")

    def __init__(self, *args, **kwargs):
        super(DiscoveryDaemon, self).__init__(*args, **kwargs)
        self.pmap_interfaces = [p for p in profile_registry.classes
                    if "get_interfaces" in profile_registry.classes[p].scripts]
        self.pmap_ip = [p for p in profile_registry.classes
                    if "get_ip_discovery" in profile_registry.classes[p].scripts]
        self.new_prefixes = []
        self.new_addresses = []
        self.address_collisions = []  # (address, vrf1, o1, vrf2, o2, a2)

    def load_config(self):
        super(DiscoveryDaemon, self).load_config()
        self.i_enabled = self.config.getboolean("interface_discovery",
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
        self.p_enabled = self.config.getboolean("prefix_discovery",
                                                "enabled")
        self.asn = AS.default_as()
        self.p_save = (self.p_enabled and
                       self.config.getboolean("prefix_discovery",
                                              "save"))
        self.p_state_map = self.get_state_map(self.config.get("prefix_discovery",
                                                              "change_state"))
        self.ip_enabled = self.config.getboolean("ip_discovery",
                                                "enabled")
        self.asn = AS.default_as()
        self.ip_save = (self.ip_enabled and
                        self.config.getboolean("ip_discovery",
                                               "save"))
        self.ip_reschedule_interval = self.config.getint("ip_discovery",
                                                        "reschedule_interval")
        self.ip_concurrency = self.config.getint("ip_discovery",
                                                "concurrency")
        self.ip_success_retry = self.config.getint("ip_discovery",
                                                  "success_retry")
        self.ip_failed_retry = self.config.getint("ip_discovery",
                                                 "failed_retry")
        self.ip_success_retry_range = (int(self.ip_success_retry * 0.9),
                                      int(self.ip_success_retry * 1.1))
        self.ip_failed_retry_range = (int(self.ip_failed_retry * 0.9),
                                     int(self.ip_failed_retry * 1.1))
        self.ip_state_map = self.get_state_map(self.config.get("prefix_discovery",
                                                              "change_state"))
        # Templates
        self.fqdn_template = self.config.get("ip_discovery",
                                             "fqdn_template")
        if self.fqdn_template:
            self.fqdn_template = Template(self.fqdn_template)

    def get_state_map(self, s):
        """
        Process from state -> to state; ....; from state -> to state syntax
        and return a map of {state: state}
        :param s:
        :return:
        """
        def get_state(name):
            try:
                return ResourceState.objects.get(name=name)
            except ResourceState.DoesNotExist:
                self.die("Unknown resource state: '%s'" % name)

        m = {}
        for x in s.split(";"):
            x = x.strip()
            if not x:
                continue
            if "->" not in x:
                self.die("Invalid state map expression: '%s'" % x)
            f, t = [get_state(y.strip()) for y in x.split("->")]
            m[f.id] = t
        return m

    def run(self):
        last_i_check = 0
        last_ip_check = 0
        interface_discovery_task = None
        ip_discovery_task = None
        self.reset_vrf_cache()
        while True:
            if self.new_prefixes:
                self.report_new_prefixes()
                self.new_prefixes = []
            if self.new_addresses:
                self.report_new_addresses()
                self.new_addresses = []
            if self.address_collisions:
                self.report_address_collisions()
                self.address_collisions = []
            reset_queries()
            now = time.time()
            if self.i_enabled:
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
            if self.ip_enabled:
                # IP discovery
                if now - last_ip_check >= self.ip_reschedule_interval:
                    # Schedule new objects to discover
                    self.schedule_ip_discovery()
                    last_ip_check = time.time()
                if ip_discovery_task is None:
                    # Start new ip discovery round
                    ip_discovery_task = self.run_ip_discovery()
                else:
                    # Check discovery is completed
                    try:
                        r = ip_discovery_task.get_result(block=False)
                    except ReduceTask.NotReady:
                        r = None
                    if r:
                        self.process_ip_discovery(r)
                        ip_discovery_task = None
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
                if type(v) != int or not hasattr(vv, "id") or v != vv.id:
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
                    .order_by("next_check")\
                    .only("managed_object").limit(self.i_concurrency)]
        if ido:
            logging.info("Running interface discovery for %s" % ", ".join([o.name for o in ido]))
            task = ReduceTask.create_task(ido,
                    interface_discovery_reduce, {},
                    "get_interfaces", {})
            return task
        else:
            return None

    def run_ip_discovery(self):
        """
        Run IP discovery round
        :rtype: Reduce Task
        :return:
        """
        ido = [s.managed_object
               for s in DiscoveryStatusIP.objects\
                    .filter(next_check__lte=datetime.datetime.now())\
                    .order_by("next_check")\
                    .only("managed_object").limit(self.ip_concurrency)]
        if ido:
            logging.info("Running IP discovery for %s" % ", ".join([o.name for o in ido]))
            task = ReduceTask.create_task(ido,
                    interface_discovery_reduce, {},
                    "get_ip_discovery", {})
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

    def process_ip_discovery(self, r):
        """
        Process IP discovery results
        """
        for o, status, result in r:
            if status == "C":
                try:
                    self.import_ip(o, result)
                except:
                    error_report()
                DiscoveryStatusIP.reschedule(o,
                    random.randint(*self.ip_success_retry_range), True)
            else:
                self.o_info(o, "get_interfaces failed: %s" % result)
                DiscoveryStatusIP.reschedule(o,
                    random.randint(*self.ip_failed_retry_range), False)

    def reset_vrf_cache(self):
        """
        Cleanup VRF cache
        :return:
        """
        self.cache_vrf_by_rd = {}
        self.cache_vrf_by_name = {}

    def get_or_create_VRF(self, object, name, rd):
        """

        :param object:
        :param name:
        :param rd:
        :return:
        """
        def set_cache(vrf):
            self.cache_vrf_by_rd[vrf.rd] = vrf
            self.cache_vrf_by_name[vrf.name] = vrf
            return vrf

        if name == "default":
            if object.vrf:
                # Use object's VRF is set
                return object.vrf
            # Get default VRF
            try:
                return self.cache_vrf_by_name["default"]
            except KeyError:
                return set_cache(VRF.get_global())
        # Non-default VRF
        # Lookup RD cache
        try:
            return self.cache_vrf_by_rd[rd]
        except KeyError:
            pass
        # Lookup database
        try:
            return set_cache(VRF.objects.get(rd=rd))
        except VRF.DoesNotExist:
            pass
        # VRF Not found, create
        # Generate unique VRF in case of names clash
        vrf_name = name
        if VRF.objects.filter(name=vrf_name).exists():
            # Name clash, generate new name by appending RD
            vrf_name += "_%s" % rd
            self.o_info(object, "Conflicting names for VRF %s. Using fallback name %s" % (name, vrf_name))
        # Create VRF
        vrf = VRF(name=vrf_name,
            rd=rd,
            vrf_group=VRF.get_global().vrf_group
        )
        vrf.save()
        return set_cache(vrf)

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
                        "name": fi["forwarding_instance"]
                    })
                    self.log_changes(o, "Forwarding instance '%s' has been changed" % forwarding_instance,
                                     changes)
                else:
                    # Create forwarding instance
                    self.o_info(o, "Creating forwarding instance '%s'" % fi["forwarding_instance"])
                    vr = fi["virtual_router"] if "virtual_router" in fi else None
                    forwarding_instance = ForwardingInstance(
                        managed_object=o.id,
                        name=fi["forwarding_instance"],
                        type=fi["type"],
                        virtual_router=vr)
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
                # Remove hanging subinterfaces
                q = Q(interface=iface.id)
                if forwarding_instance:
                    q &= Q(forwarding_instance=forwarding_instance.id)
                else:
                    q &= (Q(forwarding_instance__exists=False) |
                          Q(forwarding_instance=None))
                e_subs = set(str(s.name) for s in
                             SubInterface.objects.filter(q).only("name"))
                f_subs = set(str(x["name"]) for x in i["subinterfaces"])
                for si_name in e_subs - f_subs:
                    self.o_info(o, "Deleting subinterface '%s'" % si_name)
                    x = SubInterface.objects.filter(interface=iface.id,
                                                    name=si_name).first()
                    if x:
                        x.delete()
                # Install subinterfaces
                for si in i["subinterfaces"]:
                    s_iface = SubInterface.objects.filter(interface=iface.id,
                            name=si["name"]).first()
                    if s_iface:
                        changes = self.update_if_changed(s_iface, {
                            "managed_object": o.id,
                            "description": si.get("description"),
                            "mac": si.get("mac", i.get("mac")),
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
                            "ifindex": si.get("snmp_ifindex"),
                            "forwarding_instance": forwarding_instance
                        })
                        self.log_changes(o, "Subinterface '%s' has been changed" % si["name"],
                                         changes)
                        # refreshed = bool(changes)
                    else:
                        self.o_info(o, "Creating subinterface '%s'" % si["name"])
                        s_iface = SubInterface(
                            interface=iface.id,
                            managed_object=o.id,
                            name=si["name"],
                            description=si.get("description"),
                            mac=si.get("mac", i.get("mac")),
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
                            ifindex=si.get("snmp_ifindex"),
                            forwarding_instance=forwarding_instance
                        )
                        s_iface.save()
                        # refreshed = True
                    si_count += 1
                    # Run prefix discovery when necessary
                    if (self.p_save and  # refreshed and
                        (si.get("is_ipv4") or si.get("is_ipv6"))):
                        self.refresh_prefix(o, fi["forwarding_instance"],
                                            fi.get("rd", "0:0"), si)
        # Remove hanging interfaces
        db_interfaces = set([x.name for x in
                Interface.objects.filter(managed_object=o.id).only("name")])
        for i in db_interfaces - found_interfaces:
            iface = Interface.objects.filter(managed_object=o.id, name=i).first()
            if iface:
                self.o_info(o, "Delete interface '%s'" % iface.name)
                SubInterface.objects.filter(interface=iface.id).delete()
                iface.delete()
        # @todo: Remove hanging forwarding instances
        self.o_info(o, "summary: %d forwarding instances, %d interfaces, %d subinterfaces" % (
            len(interfaces), len(found_interfaces), si_count))

    def import_ip(self, o, result):
        octx = self.get_object_context(o)
        for v in result:
            vrf = self.get_or_create_VRF(o, v["name"], v.get("rd", "0:0"))
            if vrf is None:
                self.o_info(o, "Skipping unknown VRF '%s'" % v["name"])
                continue
            for a in v["addresses"]:
                # Skip broadcast MACs
                if a.get("mac") == "FF:FF:FF:FF:FF:FF":
                    continue
                # Check address in IPAM
                try:
                    address = Address.objects.get(vrf=vrf, afi=a["afi"],
                                                  address=a["ip"])
                except Address.DoesNotExist:
                    address = None
                    self.notify_new_address(vrf=vrf, address=a["ip"],
                        object=o, interface=a["interface"],
                        description=None)
                if self.ip_save:
                    if address:
                        if address.state.id in self.ip_state_map:
                            # Change address state
                            fs = address.state
                            ts = self.ip_state_map[fs.id]
                            self.o_info(o,
                                        "Changing address %s:%s state from %s to %s" % (
                                            address.vrf.name, address.address,
                                            fs.name, ts.name
                                        ))
                            address.state = ts
                            address.save()
                    else:
                        if a["afi"] == "4" and not vrf.afi_ipv4:
                            self.o_info(o, "Enabling IPv4 AFI on VRF %s (%s)" % (
                                vrf.name, vrf.rd))
                            vrf.afi_ipv4 = True
                            vrf.save()
                        if a["afi"] == "6" and not vrf.afi_ipv6:
                            self.o_info(o, "Enabling IPv6 AFI on VRF %s (%s)" % (
                                vrf.name, vrf.rd))
                            vrf.afi_ipv6 = True
                            vrf.save()
                        # Check constraints and save address
                        if self.check_address_constraint(vrf, a["afi"],
                            a["ip"], o, a["interface"]):
                            Address(vrf=vrf, afi=a["afi"],
                                fqdn=self.get_fqdn(octx, a["interface"], a["ip"]),
                                mac=a["mac"], address=a["ip"],
                                description="Seen at %s:%s" % (o, a["interface"])
                            ).save()

    def schedule_interface_discovery(self):
        logging.info("Rescheduling interface discovery")
        for o in ManagedObject.objects.filter(is_managed=True,
                                    profile_name__in=self.pmap_interfaces):
            s = DiscoveryStatusInterface.objects.filter(managed_object=o.id).first()
            if not s:
                self.o_info(o, "Initial scheduling for interface discovery")
                DiscoveryStatusInterface.reschedule(o,
                    random.randint(0, self.config.getint("interface_discovery",
                                                         "failed_retry")))

    def schedule_ip_discovery(self):
        logging.info("Rescheduling ip discovery")
        for o in ManagedObject.objects.filter(is_managed=True,
                                    profile_name__in=self.pmap_ip):
            s = DiscoveryStatusIP.objects.filter(managed_object=o.id).first()
            if not s:
                self.o_info(o, "Initial scheduling for ip discovery")
                DiscoveryStatusIP.reschedule(o,
                    random.randint(0, self.config.getint("ip_discovery",
                                                         "failed_retry")))

    def refresh_prefix(self, o, vrf_name, rd, si):
        """
        Refresh IPAM address and prefixes
        :param o: Managed Object instance
        :type o: ManagedObject
        :param o: VRF
        :type o: VRF
        :param si: SubInterface description
        :type si: dict
        :return:
        """
        vrf = self.get_or_create_VRF(o, vrf_name, rd)
        octx = self.get_object_context(o)
        ipv4_addresses = si.get("ipv4_addresses", [])
        ipv6_addresses = [a for a in si.get("ipv6_addresses", [])
                          if not a.startswith("fe80:")]
        addresses = ipv4_addresses + ipv6_addresses
        if vrf is None:
            p = set(str(IP.prefix(a).normalized) for a in addresses)
            self.o_info(o, "Cannot find VRF for prefixes: %s" % ", ".join(p))
            return
        seen = set()
        for a in addresses:
            p = IP.prefix(a)
            prefix = str(p.normalized)
            # Ignore local prefixes
            if ((p.afi == "4" and (
                    prefix.startswith("127.") or
                    prefix.endswith("/32"))
                ) or
                (p.afi == "6" and (
                    prefix.startswith("fe80:") or
                    prefix.endswith("/128"))
                )):
                continue
            # Check prefix exists in IPAM
            if prefix not in seen:
                seen.add(prefix)
                try:
                    pfx = Prefix.objects.get(vrf=vrf, afi=p.afi, prefix=prefix)
                except Prefix.DoesNotExist:
                    pfx = None
                    # Notify about new prefix found
                    self.notify_new_prefix(vrf=vrf, prefix=a,
                        object=o, interface=si["name"],
                        description=si.get("description"))
                if self.p_save:
                    if pfx:
                        # Prefix exists
                        if pfx.state.id in self.p_state_map:
                            # Change prefix state
                            fs = pfx.state
                            ts = self.p_state_map[fs.id]
                            self.o_info(o,
                                        "Changing prefix %s:%s state from %s to %s" % (
                                            pfx.vrf.name, pfx.prefix,
                                            fs.name, ts.name
                                        ))
                            pfx.state = ts
                            pfx.save()
                    else:
                        # Create prefix
                        Prefix(vrf=vrf, afi=p.afi, asn=self.asn,
                            prefix=prefix,
                            description=si.get("description")).save()
            # Check address exists in IPAM
            # @todo: MAC
            try:
                a = Address.objects.get(vrf=vrf, afi=p.afi, address=p.address)
            except Address.DoesNotExist:
                a = None
                self.notify_new_address(vrf=vrf, address=p.address,
                    object=o, interface=si["name"],
                    description=si.get("description"))
            if a is None:
                # Create new address
                if self.ip_save:
                    if self.check_address_constraint(vrf, p.afi, p.address,
                        o, si["name"]):
                        Address(
                            vrf=vrf,
                            afi=p.afi,
                            address=p.address,
                            fqdn=self.get_fqdn(octx, si["name"], p.address),
                            mac=si.get("mac"),
                            managed_object=o,
                            description="%s:%s" % (o, si["name"])
                        ).save()
            else:
                if a.managed_object != o:
                    # Rebind
                    self.o_info(o, "Bind to %s: %s" % (vrf, p.address))
                    a.managed_object = o
                    a.description = "%s:%s" % (o, si["name"])
                    a.save()
        # Dual-stacking detection
        if addresses and len(ipv4_addresses) == len(ipv6_addresses):
            for ipv4, ipv6 in zip(ipv4_addresses, ipv6_addresses):
                try:
                    p4 = Prefix.objects.get(vrf=vrf, afi="4",
                                    prefix=str(IP.prefix(ipv4).normalized))
                    p6 = Prefix.objects.get(vrf=vrf, afi="6",
                                    prefix=str(IP.prefix(ipv6).normalized))
                except Prefix.DoesNotExist:
                    continue
                if not p4.has_transition and not p6.has_transition:
                    self.o_info(o, "Dual-stacking prefixes %s and %s" % (
                        p4, p6))
                    p4.ipv6_transition = p6
                    p4.save()

    def check_address_constraint(self, vrf, afi, address, o, i):
        """
        Check address constraints
        :param vrf:
        :param address:
        :return:
        """
        # Ignore local addresses (127.0.0.0/8 and ::1)
        if ((afi == "4" and address.startswith("127.")) or
            (afi == "6" and address == "::1")):
            return False
        # @todo: speedup
        if vrf.vrf_group.address_constraint != "G":
            return True
        # Check address does not exists in VRF group
        try:
            a = Address.objects.get(afi=afi,
                address=address,
                vrf__in=vrf.vrf_group.vrf_set.exclude(id=vrf.id))
        except Address.DoesNotExist:
            return True
        # Collision detected
        self.o_info(o, "Address collision detected: %s:%s conflicts with VRF %s" % (
            vrf, address, a.vrf
        ))
        self.address_collisions += [(address, a.vrf, a.managed_object, vrf, o, i)]
        return False

    def notify_new_prefix(self, vrf, prefix, object, interface, description):
        self.new_prefixes += [{
            "vrf": vrf,
            "prefix": prefix,
            "object": object,
            "interface": interface,
            "description": description
        }]
        self.o_info(object, "Discovered prefix %s: %s at %s" % (
            vrf, prefix, interface))

    def notify_new_address(self, vrf, address, object, interface, description):
        self.new_addresses += [{
            "vrf": vrf,
            "address": address,
            "object": object,
            "interface": interface,
            "description": description
        }]
        self.o_info(object, "Discovered address %s: %s at %s" % (
            vrf, address, interface))

    def report_new_prefixes(self):
        c = len(self.new_prefixes)
        subject = "%d new prefixes discovered" % c
        body = ["%d new prefixes discovered" % c, ""]
        for r in self.new_prefixes:
            body += ["%s: %s%sat %s:%s" % (r["vrf"], r["prefix"],
                " [%s] " % r["description"] if r["description"] else "",
                r["object"].name, r["interface"])]
        SystemNotification.notify("inv.prefix_discovery", subject=subject,
            body="\n".join(body))

    def report_new_addresses(self):
            c = len(self.new_addresses)
            subject = "%d new addresses discovered" % c
            body = ["%d new addresses discovered" % c, ""]
            for r in self.new_addresses:
                body += ["%s: %s%s at %s:%s" % (r["vrf"], r["address"],
                    " [%s] " % r["description"] if r["description"] else "",
                    r["object"].name, r["interface"])]
            SystemNotification.notify("inv.prefix_discovery", subject=subject,
                body="\n".join(body))

    def report_address_collisions(self):
        c = len(self.address_collisions)
        subject = "%d address collisions found" % c
        body = ["%d address collisions found" % c, ""]
        for address, vrf1, o1, vrf2, o2, i2 in self.address_collisions:
            r = "%s:" % address
            if o1:
                r += " %s (%s)" % (vrf1, o1)
            else:
                r += " %s" % vrf1
            r += " vs "
            r += "%s (%s:%s)" % (vrf2, o2, i2)
            body += [r]
        SystemNotification.notify("inv.prefix_discovery", subject=subject,
            body="\n".join(body))

    def get_object_context(self, o):
        """
        Generate object part of context for get_fqdn
        :param o:
        :return:
        """
        name = o.name
        if "." in name:
            host, domain = name.split(".", 1)
        else:
            host = name
            domain = None
        return {
            "object": o,
            "name": name,
            "host": host,
            "domain": domain
        }

    def get_fqdn(self, octx, interface, address):
        """
        Generate FQDN for address
        :return:
        """
        afi = "6" if ":" in address else "4"
        if afi == "4":
            ip = [str(x) for x in IP.prefix(address)._get_parts()]
        else:
            ip = ["%x" % x for x in IP.prefix(address)._get_parts()]
        rip = list(reversed(ip))
        c = octx.copy()
        c.update({
            "afi": afi,
            "IP": ip,
            "rIP": rip,
            "interface": interface,
        })
        return self.fqdn_template.render(Context(c))


def interface_discovery_reduce(task):
    return [(t.managed_object, t.status, t.script_result)
            for t in task.maptask_set.all()]
