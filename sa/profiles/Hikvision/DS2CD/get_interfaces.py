# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DS2CD.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import xml.etree.ElementTree as ElementTree
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4, IPv6
from noc.core.script.http.base import HTTPError


class Script(BaseScript):
    name = "Hikvision.DS2CD.get_interfaces"
    interface = IGetInterfaces

    def execute(self):
        r = []
        ns = {'ns': 'urn:psialliance-org'}
        v = self.http.get("/PSIA/System/Network/interfaces", cached=True, use_basic=True)
        root = ElementTree.fromstring(v)
        # mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        for o in root:
            o_id = o.find("ns:id", ns).text
            name = "eth%s" % o_id
            iface = {
                "name": name,
                "type": "physical",
                "admin_status": True,
                "oper_status": True
            }
            sub = {
                "name": name,
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": []
            }
            exten = o.find("ns:Extensions", ns)
            link = exten.find("ns:Link", ns)
            mac = link.find("ns:MACAddress",ns).text
            #mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]

            if mac:
                sub["mac"] = mac
                iface["mac"] = mac
            ip = o.find("ns:IPAddress", ns)
            print ip
            # for ip in ip_addresses:
            afi = ip.find("ns:ipVersion", ns).text
            if afi in ["v4", "dual"]:
                if "IPv4" not in sub["enabled_afi"]:
                    sub["enabled_afi"] += ["IPv4"]
                ip_address = "%s/%s" % (
                    ip.find("ns:ipAddress", ns).text, IPv4.netmask_to_len(
                        ip.find("ns:subnetMask", ns).text
                    )
                )
                if "ipv4_addresses" in sub:
                    sub["ipv4_addresses"] += [ip_address]
                else:
                    sub["ipv4_addresses"] = [ip_address]
            if afi in ["v6"]:
                if "IPv6" not in sub["enabled_afi"]:
                    sub["enabled_afi"] += ["IPv6"]
                ip_address = IPv6(
                    ip.find("ns:ipAddress", ns).text, netmask=ip.find("ns:subnetMask", ns).text
                ).prefix

            iface["subinterfaces"] = [sub]
            r += [iface]

        return [{"interfaces": r}]
