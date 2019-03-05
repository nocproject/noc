# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DSKV8.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import xml.etree.ElementTree as ElementTree
from copy import copy
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4, IPv6


class Script(BaseScript):
    name = "Hikvision.DSKV8.get_interfaces"
    cache = True
    interface = IGetInterfaces

    def xml_2_dict(self, r, root=True):
        if root:
            t = r.tag.split("}")[1][0:]
            return {t: self.xml_2_dict(r, False)}
        d = copy(r.attrib)
        if r.text:
            d["_text"] = r.text
        for x in r.findall("./*"):
            t = x.tag.split("}")[1][0:]
            if t not in d:
                d[t] = []
            d[t].append(self.xml_2_dict(x, False))
        return d

    def execute(self):
        r = []
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        v = self.http.get("/ISAPI/System/Network/interfaces", json=False, cached=True, use_basic=True)
        root = ElementTree.fromstring(v)
        v = self.xml_2_dict(root)
        interfaces = v['NetworkInterfaceList']['NetworkInterface']
        i = 0
        for o in interfaces:
            iface = {
                "name": "eth%d" % i,
                "type": "physical",
                "admin_status": True,
                "oper_status": True,
                "mac": mac
            }
            sub = {
                "name": "eth%d" % i,
                "admin_status": True,
                "oper_status": True,
                "mac": mac,
                "enabled_afi": [],
            }
            for ip in o['IPAddress']:
                afi = ip['ipVersion'][0]["_text"]
                if afi == "v4":
                    if "IPv4" not in sub["enabled_afi"]:
                        sub["enabled_afi"] += ["IPv4"]
                    ip_address = "%s/%s" % (
                        ip['ipAddress'][0]["_text"], IPv4.netmask_to_len(
                            ip['subnetMask'][0]["_text"]
                        )
                    )
                    if "ipv4_addresses" in sub:
                        sub["ipv4_addresses"] += [ip_address]
                    else:
                        sub["ipv4_addresses"] = [ip_address]
                if afi == "v6":
                    if "IPv6" not in sub["enabled_afi"]:
                        sub["enabled_afi"] += ["IPv6"]
                    ip_address = IPv6(
                        ip['ipAddress'][0]["_text"], netmask=ip['subnetMask'][0]["_text"]
                    ).prefix

            i = i + 1
            iface["subinterfaces"] = [sub]
            r += [iface]

        return [{"interfaces": r}]
