# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWL.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "DCN.DCWL.get_interfaces"
    cache = True
    interface = IGetInterfaces

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

    @staticmethod
    def parse_block(block):
        r = {}
        for line in block.splitlines():
            line = line.split(' ', 1)
            if len(line) != 2:
                continue
            r[line[0].strip()] = line[1].strip()
        return r

    def execute(self):
        interfaces = []
        wres = {}
        w = self.cli("get radio all detail")
        for block in w.split("\n\n"):
            wr = self.parse_block(block)
            if "name" not in wr:
                continue
            wres[wr["name"]] = {"ieee_mode": self.get_interface_ieee(wr["mode"]),
                                "channel": wr["channel"],
                                "freq": self.get_interface_freq(wr["mode"]),
                                "channelbandwidth": wr["n-bandwidth"]}

        c = self.cli("get interface all detail")
        for block in c.split("\n\n"):
            r = self.parse_block(block)
            name = r.get("name")
            if "name" not in r:
                self.logger.info("Nothing name in block: %s" % block)
                continue

            iftype = self.profile.get_interface_type(name)
            if not iftype:
                self.logger.info("Ignoring unknown interface type: '%s", iftype)
                continue
            ip_address, ip_subnet = r.get("ip") or r.get("static-ip"), r.get("mask") or r.get("static-mask")

            if ("eth" in name and "mac" in r) or (ip_subnet and ip_address):
                interfaces += [{
                    "type": iftype,
                    "name": name,
                    "subinterfaces": []
                }]
                sub = {
                    "name": name,
                    "enabled_afi": [],
                }
                if r.get("mac"):
                    interfaces[-1]["mac"] = r["mac"]
                    sub["mac"] = r["mac"]
                    sub["enabled_afi"] += ["BRIDGE"]
                # ip address + ip subnet
                if ip_subnet and ip_address:
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                    sub["ipv4_addresses"] = [ip_address]
                    sub["enabled_afi"] += ["IPv4"]
                interfaces[-1]["subinterfaces"] += [sub]

        descr_template = "ssid_broadcast=%s, ieee_mode=%s, channel=%s, freq=%s, channelbandwidth=%sMHz"
        for line in c.splitlines():
            r = line.split(' ', 1)
            if r[0] == "name":
                name = r[1].strip()
            if r[0] == "mac":
                mac = r[1].strip()
            if r[0] == "ssid":
                ssid = r[1].strip().replace(" ", "").replace("Managed", "")
                if ssid.startswith("2a2d"):
                    # 2a2d - hex string
                    ssid = ssid.decode("hex")
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
