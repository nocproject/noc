# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWL.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "DCN.DCWL.get_interfaces"
    cache = True
    interface = IGetInterfaces

    INTERFACE_TYPES = {

            "lo": "loopback",  # Loopback

        }

    INTERFACE_TYPES2 = {

            "brv": "unknown",  # No comment
            "eth": "physical",  # No comment
            "wla": "physical",  # No comment

        }

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES2.get(name[:3])
        if c:
            return c
        c = cls.INTERFACE_TYPES.get(name[:2])
        return c

    FREQ = {
        "bg-n": "2400GHz",
        "a-n": "5150GHz"
    }

    @classmethod
    def get_interface_freq(cls, name):
        c = cls.FREQ.get(name)
        return c

    IEEE = {
        "bg-n": "IEEE 802.11b/g/n",
        "a-n": "IEEE 802.11a/n"
    }

    @classmethod
    def get_interface_ieee(cls, name):
        c = cls.IEEE.get(name)
        return c

    def execute(self):
        interfaces = []
        wres = {}
        w = self.cli("get radio all detail")
        for wline in w.splitlines():
            wr = wline.split(" ", 1)
            if wr[0] == "name":
                wname = wr[1].strip()
            if wr[0].strip() == "mode":
                mode = wr[1].strip()
                freq = self.get_interface_freq(mode)
                ieee_mode = self.get_interface_ieee(mode)
            if wr[0].strip() == "channel":
                channel = wr[1].strip()
            if wr[0].strip() == "n-bandwidth":
                channelbandwidth = wr[1].strip()
                wres[wname] = {"ieee_mode": ieee_mode,
                               "channel": channel, "freq": freq, "channelbandwidth": channelbandwidth}
        c = self.cli("get interface all detail")
        for line in c.splitlines():
            r = line.split(' ', 1)
            ip_address = None
            if r[0] == "name":
                name = r[1].strip()
                iftype = self.get_interface_type(name)
                if not name:
                    self.logger.info(
                        "Ignoring unknown interface type: '%s", iftype
                    )
                    continue
            if r[0] == "mac":
                mac = r[1].strip()
            if r[0] == "ip":
                ip_address = r[1].strip()
            if r[0] == "mask":
                ip_subnet = r[1].strip()
                # ip address + ip subnet
                if ip_subnet or ip_address:
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                    iface = {
                        "type": iftype,
                        "name": name,
                        "mac": mac,
                        "subinterfaces": [{
                            "name": name,
                            "mac": mac,
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [ip_address],
                        }]
                    }
                    interfaces += [iface]
                # no ip address + ip subnet
                else:
                    iface = {
                        "type": iftype,
                        "name": name,
                        "mac": mac,
                        "subinterfaces": [{
                            "name": name,
                            "mac": mac,
                            "enabled_afi": ["BRIDGE"],
                        }]
                    }
                    interfaces += [iface]
        descr_template = "ssid_broadcast=%s, ieee_mode=%s, channel=%s, freq=%s, channelbandwidth=%sMHz"
        for line in c.splitlines():
            r = line.split(' ', 1)
            if r[0] == "name":
                name = r[1].strip()
            if r[0] == "mac":
                mac = r[1].strip()
            if r[0] == "ssid":
                ssid = r[1].strip().replace(" ", "").replace("Managed", "")
            if r[0] == "bss":
                bss = r[1].strip()
                if ssid:
                    b = self.cli("get bss %s detail" % bss)
                    for line in b.splitlines():
                        rb = line.split(' ', 1)
                        if rb[0] == "radio":
                            radio = rb[1].strip()
                        if rb[0] == "ignore-broadcast-ssid":
                            sb = rb[1].strip()
                            if sb == "off":
                                ssid_broadcast = "Enable"
                            else:
                                ssid_broadcast = "Disable"
                            for ri in wres.items():
                                if ri[0] == radio:
                                    iface = {
                                        "type": "physical",
                                        "name": "%s.%s" % (name, ssid),
                                        "mac": mac,
                                        "description": descr_template % (ssid_broadcast, ri[1]["ieee_mode"],
                                                                         ri[1]["channel"], ri[1]["freq"],
                                                                         ri[1]["channelbandwidth"]),
                                        "subinterfaces": [{
                                            "name": "%s.%s" % (name, ssid),
                                            "mac": mac,
                                            "enabled_afi": ["BRIDGE"],
                                        }]
                                    }
                                    interfaces += [iface]
        return [{"interfaces": interfaces}]
