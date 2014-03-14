## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP Discovery Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.template import Template, Context
from django.db.models import Q
from django.core.cache import cache
## NOC modules
from base import Report
from noc.ip.models.address import Address
from noc.ip.models.addressrange import AddressRange
from noc.ip.models.prefix import Prefix
from noc.fm.models import NewEvent
from noc.inv.models import NewAddressDiscoveryLog
from noc.lib.ip import IP
from noc.settings import config


class IPReport(Report):
    system_notification = "inv.prefix_discovery"

    def __init__(self, job, enabled=True, to_save=False,
                 allow_prefix_restrictions=False):
        super(IPReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.ip_state_map = self.get_state_map(
            config.get("ip_discovery", "change_state"))
        t = config.get("ip_discovery", "fqdn_template")
        self.fqdn_template = Template(t) if t else None
        self.new_addresses = []
        self.collisions = []
        self.locked_ranges = {}  # VRF -> [(from ip, to ip)]
        self.allow_prefix_restrictions = allow_prefix_restrictions

    def submit(self, vrf, address, interface=None, description=None,
               mac=None):
        if not self.enabled:
            return
        afi = "6" if ":" in address else "4"
        # Skip ignored MACs
        if mac and self.is_ignored_mac(mac):
            return
        # Check ip discovery enabled by prefix settings
        if (self.allow_prefix_restrictions and
                not self.is_discovery_enabled(vrf, afi, address)):
            return
        # Check address not in locked range
        if self.is_locked_range(vrf, address):
            return
        # Check address in IPAM
        r = Address.objects.filter(vrf=vrf, afi=afi, address=address)
        if r:
            self.change_address(r[0])  # Change existing address
        else:
            self.new_address(vrf, afi, address,
                interface, description, mac)

    @classmethod
    def is_discovery_enabled(cls, vrf, afi, address):
        prefix = Prefix.get_parent(vrf, afi, address)
        k = "ip-discovery-enable-%s" % prefix.id
        ds = cache.get(k)
        if ds:
            return ds == "E"
        r = prefix.effective_ip_discovery
        cache.set(k, r, 600)
        return r == "E"

    def is_ignored_mac(self, mac):
        """
        Check MAC address must be ignored
        :param mac:
        :return:
        """
        return mac == "FF:FF:FF:FF:FF:FF"

    def is_locked_range(self, vrf, address):
        """
        Check address is within locked address range
        :param vrf:
        :param address:
        :return:
        """
        if vrf not in self.locked_ranges:
            # Build locked range cache
            q = Q(action__in=["G", "D"]) | Q(is_locked=True)
            self.locked_ranges[vrf] = [
                (f.from_address, f.to_address)
                for f in AddressRange.objects.filter(
                    vrf=vrf, is_active=True).filter(q)]
        # Try to find range
        # @todo: binary search
        for from_address, to_address in self.locked_ranges[vrf]:
            if from_address <= address <= to_address:
                return True
        return False

    def new_address(self, vrf, afi, address, interface=None,
                    description=None, mac=None):
        # Enable IPv4 AFI on VRF, if not set
        if afi == "4" and not vrf.afi_ipv4:
            self.info("Enabling IPv4 AFI on VRF %s (%s)" % (
                vrf.name, vrf.rd))
            if self.to_save:
                vrf.afi_ipv4 = True
                vrf.save()
        # Enable IPv6 AFI on VRF, if not set
        if afi == "6" and not vrf.afi_ipv6:
            self.info("Enabling IPv6 AFI on VRF %s (%s)" % (
                vrf.name, vrf.rd))
            if self.to_save:
                vrf.afi_ipv6 = True
                vrf.save()
        # Check constraints and save address
        if self.check_address_constraint(vrf, afi,
            address, interface):
            self.info("IP address found: %s:%s at %s" % (
                vrf, address, interface))
            self.new_addresses += [{
                "vrf": vrf,
                "address": address,
                "description": description,
                "object": self.object,
                "interface": interface
            }]
            if self.to_save:
                if not description:
                    description = "Seen at %s:%s" % (
                        self.object.name, interface)
                Address(vrf=vrf, afi=afi,
                    fqdn=self.get_fqdn(interface, vrf, address),
                    mac=mac, address=address,
                    description=description
                ).save()

    def change_address(self, address):
        if address.state.id in self.ip_state_map:
            # Change address state
            fs = address.state
            ts = self.ip_state_map[fs.id]
            self.info(
                "Changing address %s:%s state from %s to %s" % (
                    address.vrf.name, address.address,
                    fs.name, ts.name))
            if self.to_save:
                address.state = ts
                address.save()

    def check_address_constraint(self, vrf, afi, address, interface):
        """
        Check address constraints
        :param vrf:
        :param afi:
        :param address:
        :param interface:
        :return:
        """
        # Ignore local addresses (127.0.0.0/8 and ::1)
        if ((afi == "4" and address.startswith("127.")) or
            (afi == "6" and (
                address == "::1" or
                address.startswith("fe80:")))):
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
        self.info("Address collision detected: %s:%s conflicts with VRF %s" % (
            vrf, address, a.vrf))
        self.collisions += [(address, a.vrf, a.managed_object, vrf,
                             self.object, interface)]
        # Submit FM event
        NewEvent(
            timestamp=datetime.datetime.now(),
            managed_object=self.object,
            raw_vars={
                "source": "system",
                "process": "discovery",
                "type": "address collision",
                "address": address,
                "vrf": vrf.name,
                "interface": interface,
                "existing_vrf": a.vrf.name,
                "existing_object": a.managed_object.name if a.managed_object else None
            },
            log=[]
        ).save()
        return False

    def get_fqdn(self, interface, vrf, address):
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
        c = self.context.copy()
        c.update({
            "afi": afi,
            "IP": ip,
            "rIP": rip,
            "interface": interface,
            "vrf": vrf
        })
        return self.fqdn_template.render(Context(c))

    def send(self):
        if not (self.new_addresses or self.collisions):
            return
        # Write database log
        ts = datetime.datetime.now()
        log = [NewAddressDiscoveryLog(
            timestamp=ts,
            vrf=p["vrf"].name,
            address=p["address"],
            description=None,
            managed_object=self.object.name,
            interface=p["interface"]) for p in self.new_addresses]
        if log:
            NewAddressDiscoveryLog.objects.insert(log, load_bulk=True)
            # Send report
            ctx = {
                "count": len(self.new_addresses),
                "addresses": [
                    {
                        "vrf": a["vrf"],
                        "address": a["address"],
                        "description": None,
                        "object": self.object,
                        "interface": a["interface"]
                    } for a in self.new_addresses]
            }
            self.notify("inv.discovery.new_addresses_report", ctx)
