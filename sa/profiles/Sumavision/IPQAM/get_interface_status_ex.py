# ---------------------------------------------------------------------
# Sumavision.IPQAM.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Sumavision.IPQAM.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    SPEED = {
        "1Gbps Full": 1000000,
        "100M Full": 100000,
        "100M Half": 100000,
        "10M Full": 10000,
        "10M Half": 10000,
    }

    def execute_snmp(self, interfaces=None):
        result = []

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
            result += [
                {
                    "interface": "%s/%s" % (channel, mname),
                    "admin_status": bool(m_astatus),
                    "oper_status": m_ostatus,
                    "full_duplex": False,
                }
            ]

        for coid, cindex in self.snmp.getnext("1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.8"):
            cstatus = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.17.1.1.%s" % cindex)
            cspeed = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.19.1.1.%s" % cindex)
            cspeed = float(cspeed.rstrip("Mbps")) * 1000
            result += [
                {
                    "interface": "1/1.%s" % cindex,
                    "admin_status": cstatus > 0,
                    "oper_status": cstatus > 0,
                    "full_duplex": True,
                    "in_speed": cspeed,
                    "out_speed": cspeed,
                }
            ]

        for oid, ifindex in self.snmp.getnext("1.3.6.1.4.1.32285.2.2.10.3008.4.2.1.3"):
            status = False
            full_duplex = False
            ispeed = None
            ifname = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.4.2.1.11.1.1.%s" % ifindex)
            istatus = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.4.2.1.10.1.1.%s" % ifindex)

            if istatus not in ["Shut Down", "Link Error"]:
                status = True
            if "full" in istatus.lower():
                full_duplex = True
            if self.SPEED.get(istatus):
                ispeed = self.SPEED.get(istatus)
            result += [
                {
                    "interface": ifname,
                    "admin_status": status,
                    "oper_status": status,
                    "full_duplex": full_duplex,
                    "in_speed": ispeed,
                    "out_speed": ispeed,
                }
            ]

        return result
