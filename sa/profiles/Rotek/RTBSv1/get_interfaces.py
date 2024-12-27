# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mac import MAC
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_interfaces"
    cache = True
    interface = IGetInterfaces
    reuse_cli_session = False
    keep_cli_session = False

    rx_sh_int = re.compile(
        r"^(?P<ifindex>\d+):\s+(?P<ifname>[eltbrgaw]\S+):\s"
        r"<(?P<flags>.*?)>\s+mtu\s+(?P<mtu>\d+).+?\n"
        r"^\s+link/\S+(?:\s+(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}))?\s+.+?\n"
        r"(?:^\s+inet\s+(?P<ip>\d+\S+)\s+)?",
        re.MULTILINE | re.DOTALL,
    )
    rx_vlan = re.compile(r"\S+vlan-to-ssid: on; id:\s+(?P<vlan>\S+)")
    rx_status = re.compile(r"^(?P<status>UP|DOWN\S+)", re.MULTILINE)
    re_ath = re.compile(r"(?P<ath>ath\d)", re.MULTILINE)

    def execute_snmp(self):
        interfaces = {}
        ss = {}
        ent_oid = self.profile.get_enterprise_id(self)
        for soid, sname in self.snmp.getnext(f"1.3.6.1.4.1.{ent_oid}.3.10.1.2.1.1.4"):
            sifindex = int(soid.split(".")[-1])
            ieee_mode = self.snmp.get(f"1.3.6.1.4.1.{ent_oid}.3.10.1.2.1.1.2.{sifindex}")
            freq = self.snmp.get(f"1.3.6.1.4.1.{ent_oid}.3.10.1.2.1.1.6.{sifindex}")
            channel = self.snmp.get(f"1.3.6.1.4.1.{ent_oid}.3.10.1.2.1.1.7.{sifindex}")
            broadcast = self.snmp.get(f"1.2.840.10036.1.1.1.7.{sifindex}")
            ss[sifindex] = {
                "ssid": sname,
                "ieee_mode": ieee_mode,
                "channel": channel,
                "freq": freq,
                "broadcast": "enable" if broadcast else "disable",
            }
        print(ss)
        for v in self.snmp.getnext(mib["IF-MIB::ifIndex"]):
            ifindex = v[1]
            ifname = self.snmp.get(mib["IF-MIB::ifDescr", ifindex])
            iftype = self.profile.get_interface_type(ifname)
            if "peer" in ifname:
                continue
            if not ifname:
                self.logger.info("Ignoring unknown interface type: '%s", iftype)
                continue
            mac = self.snmp.get(mib["IF-MIB::ifPhysAddress", ifindex])
            mtu = self.snmp.get(mib["IF-MIB::ifMtu", ifindex])
            astatus = self.snmp.get(mib["IF-MIB::ifAdminStatus", ifindex])
            if astatus == 1:
                admin_status = True
            else:
                admin_status = False
            ostatus = self.snmp.get(mib["IF-MIB::ifOperStatus", ifindex])
            if ostatus == 1:
                oper_status = True
            else:
                oper_status = False
            if "." in ifname:
                ifname, vlan_ids = ifname.split(".", 1)
                if ifname in interfaces:
                    interfaces[ifname]["subinterfaces"] += [
                        {
                            "name": "%s.%s" % (ifname, vlan_ids),
                            "snmp_ifindex": ifindex,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "mtu": mtu,
                            "enabled_afi": ["BRIDGE"],
                            "vlan_ids": vlan_ids,
                        }
                    ]
            else:
                interfaces[ifname] = {
                    "type": iftype,
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "snmp_ifindex": ifindex,
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "snmp_ifindex": ifindex,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "mtu": mtu,
                            "enabled_afi": ["BRIDGE"],
                        }
                    ],
                }
            if mac:
                interfaces[ifname]["mac"] = MAC(mac)
                interfaces[ifname]["subinterfaces"][0]["mac"] = MAC(mac)
            if self.is_platform_BS24:
                for i in ss.items():
                    if int(i[0]) == ifindex:
                        vname = "%s.%s" % (ifname, i[1]["ssid"])
                        interfaces[vname] = {
                            "type": iftype,
                            "name": vname,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "snmp_ifindex": ifindex,
                            "description": "ssid_broadcast=%s, ieee_mode=%s, channel=%s, freq=%sGHz"
                            % (i[1]["broadcast"], i[1]["ieee_mode"], i[1]["channel"], i[1]["freq"]),
                            "subinterfaces": [
                                {
                                    "name": vname,
                                    "snmp_ifindex": ifindex,
                                    "admin_status": admin_status,
                                    "oper_status": oper_status,
                                    "mtu": mtu,
                                    "enabled_afi": ["BRIDGE"],
                                }
                            ],
                        }
                        if mac:
                            interfaces[vname]["mac"] = MAC(mac)
                            interfaces[vname]["subinterfaces"][0]["mac"] = MAC(mac)
        return [{"interfaces": list(interfaces.values())}]

    def execute_cli(self):
        interfaces = []
        ssid = {}
        c = self.cli("show interface list")
        ifaces = dict(item.strip().split(":") for item in c.split(";"))
        for ra_iface in ifaces["VAP(radio)"].split(","):
            match = self.re_ath.match(ra_iface.strip())
            if match:
                ath = match.group("ath")
                s = self.cli("show interface %s ssid" % ath)
                v = self.cli("show interface %s vlan-to-ssid" % ath)
                a = self.cli("show interface %s ssid-broadcast" % ath)
                i = self.cli("show interface wifi0 ieee-mode")
                c = self.cli("show interface wifi0 channel")
                f = self.cli("show interface wifi0 freq")
                res = s.split(":")[1].strip().replace('"', "")
                resv = v.split(":")[2].strip()
                ssid_broadcast = a.split(":")[1].strip()
                ieee_mode = "IEEE 802.11%s" % i.split(":")[1].strip()
                channel = c.strip().splitlines()[0].split(":")[1].strip()
                freq = f.strip().splitlines()[0].split(":")[1].strip()
                ssid[ath] = {
                    "ssid": res,
                    "vlan": resv,
                    "ssid_broadcast": ssid_broadcast,
                    "ieee_mode": ieee_mode,
                    "channel": channel,
                    "freq": freq,
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
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "mtu": mtu,
                            "admin_status": a_status,
                            "oper_status": o_status,
                            "snmp_ifindex": match.group("ifindex"),
                        }
                    ],
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
                ri = ssid.get(ifname)
                if ri:
                    if ri["ssid_broadcast"] == "on":
                        ssid_broadcast = "enable"
                    else:
                        ssid_broadcast = "disable"
                        o_status = False  # Do not touch !!!
                    iface = {
                        "type": "physical",
                        "name": "%s.%s" % (ifname, ri["ssid"]),
                        "admin_status": a_status,
                        "oper_status": o_status,
                        "mac": MAC(mac),
                        "snmp_ifindex": match.group("ifindex"),
                        "description": "ssid_broadcast=%s, ieee_mode=%s, channel=%s, freq=%sGHz"
                        % (ssid_broadcast, ri["ieee_mode"], ri["channel"], ri["freq"]),
                        "subinterfaces": [
                            {
                                "name": "%s.%s" % (ifname, ri["ssid"]),
                                "enabled_afi": ["BRIDGE"],
                                "admin_status": a_status,
                                "oper_status": o_status,
                                "mtu": mtu,
                                "mac": MAC(mac),
                                "snmp_ifindex": match.group("ifindex"),
                                "untagged_vlan": int(ri["vlan"]),
                            }
                        ],
                    }
                    interfaces += [iface]
        return [{"interfaces": interfaces}]
