## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP Discovery Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.template import Template, Context
## NOC modules
from base import Report
from noc.ip.models.address import Address
from noc.fm.models import NewEvent
from noc.inv.models import NewAddressDiscoveryLog
from noc.lib.ip import IP
from noc.settings import config


class IPReport(Report):
    system_notification = "inv.prefix_discovery"

    def __init__(self, job, enabled=True, to_save=False):
        super(IPReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.ip_state_map = self.get_state_map(
            config.get("ip_discovery", "change_state"))
        t = config.get("ip_discovery", "fqdn_template")
        self.fqdn_template = Template(t) if t else None
        self.new_addresses = []
        self.collisions = []

    def submit(self, vrf, address, interface=None, description=None,
               mac=None):
        if not self.enabled:
            return
        # Skip ignored MACs
        if mac and self.is_ignored_mac(mac):
            return
        # Check address in IPAM
        afi = "6" if ":" in address else "4"
        r = Address.objects.filter(vrf=vrf, afi=afi, address=address)
        if r:
            self.change_address(r[0])  # Change existing address
        else:
            self.new_address(vrf, afi, address,
                interface, description, mac)

    def is_ignored_mac(self, mac):
        """
        Check MAC address must be ignored
        :param mac:
        :return:
        """
        return mac == "FF:FF:FF:FF:FF:FF"

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
            if self.to_save:
                if not description:
                    description = "Seen at %s:%s" % (
                        self.object, interface)
                Address(vrf=vrf, afi=afi,
                    fqdn=self.get_fqdn(interface, address),
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
                "existing_object": a.managed_object.name
            },
            log=[]
        ).save()
        return False

    def get_fqdn(self, interface, address):
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
