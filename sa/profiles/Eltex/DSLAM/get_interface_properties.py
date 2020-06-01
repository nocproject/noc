# ----------------------------------------------------------------------
# Eltex.DSLAM.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.DSLAM.get_interface_properties"

    MAX_GETNEXT_RETIRES = 8

    def iter_interface_ifindex(self, name: str):
        if self.is_platform_MXA24:
            o = "1.3.6.1.4.1.34300.1.6"
            ooid = "%s.15.2.1.2" % o
            aoid = "%s.10.2.1.2" % o
            for oid, ifname in self.snmp.getnext(aoid, max_retries=8):
                if oid.endswith(".0"):
                    ifindex = int(oid.split(".")[-2])
                else:
                    ifindex = int(oid.split(".")[-1])
                yield "name", ifindex, ifname
            for oid, ifname in self.snmp.getnext(ooid, max_retries=8):
                if " " in ifname:
                    ifname = ifname.split()[2]
                if ifname.startswith("p"):
                    ifname = "s%s" % ifname
                if oid.endswith(".0"):
                    ifindex = int(oid.split(".")[-2])
                else:
                    ifindex = int(oid.split(".")[-1])
                yield "name", ifindex, ifname
        else:
            if self.is_platform_MXA32:
                o = "1.3.6.1.4.1.35265.1.28"
            else:
                o = "1.3.6.1.4.1.35265.1.33"
            aoid = "%s.10.2.1.2" % o
            for oid, ifname in self.snmp.getnext(
                aoid,
                max_repetitions=self.get_max_repetitions(),
                max_retries=self.get_getnext_retires(),
            ):
                if oid.endswith(".0"):
                    ifindex = int(oid.split(".")[-2])
                else:
                    ifindex = int(oid.split(".")[-1])
                yield "name", ifindex, ifname

            for oid, ifname in self.snmp.getnext(
                mib["IF-MIB::ifDescr"],
                max_repetitions=self.get_max_repetitions(),
                max_retries=self.get_getnext_retires(),
            ):
                if ifname.startswith("p"):
                    ifname = "s%s" % ifname
                ifindex = int(oid.split(".")[-1])
                yield "name", ifindex, ifname
