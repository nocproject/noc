# ---------------------------------------------------------------------
# Hikvision.DSKV8.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
    name = "Hikvision.DSKV8.get_interfaces"
    interface = IGetInterfaces

    def execute(self):
        r = []
        ns = {
            "isapi": "http://www.isapi.org/ver20/XMLSchema",
            "std-cgi": "http://www.std-cgi.com/ver20/XMLSchema",
            "hikvision": "http://www.hikvision.com/ver20/XMLSchema",
        }
        v = self.http.get("/ISAPI/System/Network/interfaces", use_basic=True)
        v = v.replace("\n", "")
        if "std-cgi" in v:
            ns["ns"] = ns["std-cgi"]
        elif "www.hikvision.com" in v:
            ns["ns"] = ns["hikvision"]
        else:
            ns["ns"] = ns["isapi"]
        root = ElementTree.fromstring(v)
        # mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        for o in root:
            o_id = o.find("{%s}id" % ns["ns"]).text
            name = "eth%s" % o_id
            iface = {
                "name": name,
                "type": "physical",
                "admin_status": True,
                "oper_status": True,
                "hints": ["noc::interface::role::uplink"],
            }
            sub = {"name": name, "admin_status": True, "oper_status": True, "enabled_afi": []}
            try:
                v = self.http.get("/ISAPI/System/Network/interfaces/%s/Link" % o_id, use_basic=True)
                v = v.replace("\n", "")
                v = ElementTree.fromstring(v)
                mac = v.find("{%s}MACAddress" % ns["ns"]).text
            except HTTPError:
                mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]

            if mac:
                sub["mac"] = mac
                iface["mac"] = mac
            ip = o.find("{%s}IPAddress" % ns["ns"])
            # for ip in ip_addresses:
            afi = ip.find("{%s}ipVersion" % ns["ns"]).text
            if afi == "v4":
                if "IPv4" not in sub["enabled_afi"]:
                    sub["enabled_afi"] += ["IPv4"]
                ip_address = "%s/%s" % (
                    ip.find("{%s}ipAddress" % ns["ns"]).text,
                    IPv4.netmask_to_len(ip.find("{%s}subnetMask" % ns["ns"]).text),
                )
                if "ipv4_addresses" in sub:
                    sub["ipv4_addresses"] += [ip_address]
                else:
                    sub["ipv4_addresses"] = [ip_address]
            if afi == "v6":
                if "IPv6" not in sub["enabled_afi"]:
                    sub["enabled_afi"] += ["IPv6"]
                ip_address = IPv6(
                    ip.find("{%s}ipAddress" % ns["ns"]).text,
                    netmask=ip.find("ns:subnetMask", ns).text,
                ).prefix

            iface["subinterfaces"] = [sub]
            r += [iface]

        return [{"interfaces": r}]
