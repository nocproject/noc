# ----------------------------------------------------------------------
# Sumavision.IPQAM.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.ip import IPv4
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Sumavision.IPQAM.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def status(self, index):
        return self.snmp.get("1.3.6.1.4.1.51315.1.%s.0" % index, cached=True)

    def execute_snmp(self):
        interfaces = []

        v = {v[0]: v[1] for v in self.snmp.get_tables(["1.3.6.1.4.1.32285.2.2.10.3008.4.2"])}
        for moid, mindex in self.snmp.getnext("1.3.6.1.4.1.32285.2.2.10.3008.5.6.1.4"):
            channel = moid.split(".")[-2::][0]
            mname = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.6.1.5.1.1.%s.%s" % (channel, mindex)
            )
            m_astatus = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.6.1.7.1.1.%s.%s" % (channel, mindex)
            )
            try:
                minname = self.snmp.get(
                    "1.3.6.1.4.1.32285.2.2.10.3008.4.6.1.8.1.1.%s.%s" % (channel, mindex)
                )
                if minname and mname == minname and m_astatus:
                    m_ostatus = True
                else:
                    m_ostatus = False
            except self.snmp.SNMPError:
                m_ostatus = False
            interfaces += [
                {
                    "type": "physical",
                    "name": "%s/%s" % (channel, mname),
                    "admin_status": bool(m_astatus),
                    "oper_status": m_ostatus,
                    "snmp_ifindex": int("%s%s" % (channel, mindex)),
                    "description": "",
                    "subinterfaces": [],
                }
            ]
        for coid, cindex in self.snmp.getnext("1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.8"):
            cstatus = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.17.1.1.%s" % cindex)
            freq = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.4.1.1.%s" % cindex)
            interfaces += [
                {
                    "type": "physical",
                    "name": "1/1.%s" % cindex,
                    "admin_status": cstatus > 0,
                    "oper_status": cstatus > 0,
                    "snmp_ifindex": cindex,
                    "description": "",
                    "subinterfaces": [{"name": freq, "description": "1/1.%s" % cindex}],
                }
            ]

        for oid, ifindex in self.snmp.getnext("1.3.6.1.4.1.32285.2.2.10.3008.4.2.1.3"):
            ifname = v["1.11.1.1.%s" % ifindex]
            status = False
            if v["1.10.1.1.%s" % ifindex] not in ["Shut Down", "linkError"]:
                status = True
            ip_address = v["1.4.1.1.%s" % ifindex]
            ip_subnet = v["1.5.1.1.%s" % ifindex]
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            interfaces += [
                {
                    "type": "physical",
                    "name": ifname,
                    "admin_status": status,
                    "oper_status": status,
                    "snmp_ifindex": ifindex,
                    "mac": v["1.7.1.1.%s" % ifindex],
                    "description": "",
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": status,
                            "oper_status": status,
                            "snmp_ifindex": ifindex,
                            "mac": v["1.7.1.1.%s" % ifindex],
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [ip_address],
                        }
                    ],
                }
            ]

        return [{"interfaces": interfaces}]
