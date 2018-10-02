# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_interfaces"
    cache = True
    interface = IGetInterfaces
    reuse_cli_session = False
    keep_cli_session = False

    rx_sh_int = re.compile(
        r"^(?P<ifindex>\d+):\s+(?P<ifname>(e|l|t|b|r|g|a)\S+):\s"
        r"<(?P<flags>.*?)>\s+mtu\s+(?P<mtu>\d+).+?\n"
        r"^\s+link/\S+(?:\s+(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}))?\s+.+?\n"
        r"(?:^\s+inet\s+(?P<ip>\d+\S+)\s+)?",
        re.MULTILINE | re.DOTALL)
    rx_vlan = re.compile(r"\S+vlan-to-ssid: on; id:\s+(?P<vlan>\S+)")
    rx_status = re.compile(r"^(?P<status>UP|DOWN\S+)", re.MULTILINE)

    def execute_snmp(self):
        interfaces = []
        ss = {}
        for soid, sname in self.snmp.getnext("1.3.6.1.4.1.41752.3.10.1.2.1.1.4"):
            sifindex = int(soid.split(".")[-1])
            ieee_mode = self.snmp.get("1.3.6.1.4.1.41752.3.10.1.2.1.1.2.%s" % sifindex)
            freq = self.snmp.get("1.3.6.1.4.1.41752.3.10.1.2.1.1.6.%s" % sifindex)
            channel = self.snmp.get("1.3.6.1.4.1.41752.3.10.1.2.1.1.7.%s" % sifindex)
            ss[sifindex] = {
                "ssid": sname, "ieee_mode": ieee_mode,
                "channel": channel, "freq": freq
            }
        for v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.1", cached=True):
            ifindex = v[1]
            name = self.snmp.get("1.3.6.1.2.1.2.2.1.2.%s" % str(ifindex))
            iftype = self.profile.get_interface_type(name)
            if "peer" in name:
                continue
            if not name:
                self.logger.info("Ignoring unknown interface type: '%s", iftype)
                continue
            mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.%s" % str(ifindex))
            mtu = self.snmp.get("1.3.6.1.2.1.2.2.1.4.%s" % str(ifindex))
            astatus = self.snmp.get("1.3.6.1.2.1.2.2.1.7.%s" % str(ifindex))
            if astatus == 1:
                admin_status = True
            else:
                admin_status = False
            ostatus = self.snmp.get("1.3.6.1.2.1.2.2.1.8.%s" % str(ifindex))
            if ostatus == 1:
                oper_status = True
            else:
                oper_status = False
            iface = {
                "type": iftype,
                "name": name,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "snmp_ifindex": ifindex,
                "subinterfaces": [{
                    "name": name,
                    "snmp_ifindex": ifindex,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "mtu": mtu,
                    "enabled_afi": ["BRIDGE"]
                }]
            }
            if mac:
                iface["mac"] = MAC(mac)
                iface["subinterfaces"][0]["mac"] = MAC(mac)
            interfaces += [iface]
            for i in ss.items():
                if int(i[0]) == ifindex:
                    a = self.cli("show interface %s ssid-broadcast" % name)
                    sb = a.split(":")[1].strip()
                    if sb == "on":
                        ssid_broadcast = "enable"
                    else:
                        ssid_broadcast = "disable"
                        oper_status = False  # Do not touch !!!
                    vname = "%s.%s" % (name, i[1]["ssid"])
                    iface = {
                        "type": iftype,
                        "name": vname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "snmp_ifindex": ifindex,
                        "description": "ssid_broadcast=%s, ieee_mode=%s, channel=%s, freq=%sGHz" % (
                            ssid_broadcast, i[1]["ieee_mode"], i[1]["channel"], i[1]["freq"]
                        ),
                        "subinterfaces": [{
                            "name": vname,
                            "snmp_ifindex": ifindex,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "mtu": mtu,
                            "enabled_afi": ["BRIDGE"]
                        }]
                    }
                    if mac:
                        iface["mac"] = MAC(mac)
                        iface["subinterfaces"][0]["mac"] = MAC(mac)
                    interfaces += [iface]
        return [{"interfaces": interfaces}]

    def execute_cli(self):
        interfaces = []
        ssid = {}
        i = ["ath0", "ath2"]
        for ri in i:
            s = self.cli("show interface %s ssid" % ri)
            v = self.cli("show interface %s vlan-to-ssid" % ri)
            a = self.cli("show interface %s ssid-broadcast" % ri)
            i = self.cli("show interface wifi0 ieee-mode")
            c = self.cli("show interface wifi0 channel")
            f = self.cli("show interface wifi0 freq")
            res = s.split(":")[1].strip().replace("\"", "")
            resv = v.split(":")[2].strip()
            ssid_broadcast = a.split(":")[1].strip()
            ieee_mode = "IEEE 802.11%s" % i.split(":")[1].strip()
            channel = c.splitlines()[0].split(":")[1].strip()
            freq = f.splitlines()[0].split(":")[1].strip()
            ssid[ri] = {
                "ssid": res, "vlan": resv, "ssid_broadcast": ssid_broadcast, "ieee_mode": ieee_mode,
                "channel": channel, "freq": freq
            }
        with self.profile.shell(self):
            v = self.cli("ip a", cached=True)
            for match in self.rx_sh_int.finditer(v):
                a_status = True
                ifname = match.group("ifname")
                if "@" in ifname:
                    ifname = ifname.split("@")[0]
                flags = match.group("flags")
                smatch = self.rx_status.search(flags)
                if smatch:
                    o_status = smatch.group("status").lower() == "up"
                else:
                    o_status = True
                ip = match.group("ip")
                mac = match.group("mac")
                mtu = match.group("mtu")
                iface = {
                    "type": self.profile.get_interface_type(ifname),
                    "name": ifname,
                    "admin_status": a_status,
                    "oper_status": o_status,
                    "snmp_ifindex": match.group("ifindex"),
                    "subinterfaces": [{
                        "name": ifname,
                        "mtu": mtu,
                        "admin_status": a_status,
                        "oper_status": o_status,
                        "snmp_ifindex": match.group("ifindex"),

                    }]
                }
                if mac:
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["mac"] = mac
                if ip:
                    iface["subinterfaces"][0]["address"] = ip
                    iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
                else:
                    iface["subinterfaces"][0]["enabled_afi"] = ["BRIDGE"]
                interfaces += [iface]
            for ri in ssid.items():
                if ifname in ri[0]:
                    iface = {
                        "type": "physical",
                        "name": "%s.%s" % (ifname, ri[1]["ssid"]),
                        "admin_status": a_status,
                        "oper_status": o_status,
                        "mac": MAC(mac),
                        "snmp_ifindex": match.group("ifindex"),
                        "description": "ssid_broadcast=%s, ieee_mode=%s, channel=%s, freq=%s" % (ri[1]["ssid_broadcast"], ri[1]["ieee_mode"], ri[1]["channel"], ri[1]["freq"]),
                        "subinterfaces": [{
                            "name": "%s.%s" % (ifname, ri[1]["ssid"]),
                            "enabled_afi": ["BRIDGE"],
                            "admin_status": a_status,
                            "oper_status": o_status,
                            "mtu": mtu,
                            "mac": MAC(mac),
                            "snmp_ifindex": match.group("ifindex"),
                            "untagged_vlan": int(ri[1]["vlan"]),
                        }]
                    }
                    interfaces += [iface]
        return [{"interfaces": interfaces}]
