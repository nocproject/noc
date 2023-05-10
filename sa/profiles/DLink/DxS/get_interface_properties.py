# ----------------------------------------------------------------------
# DLink.DxS.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DxS.get_interface_properties"

    def get_max_repetitions(self):
        if self.is_dgs:
            return 20
        return self.MAX_REPETITIONS

    def iter_interface_ifindex(self, name: str):
        ifnames = {}
        unknown_interfaces = []
        old_dlink = False
        for oid, ifname in self.snmp.getnext(
            mib["IF-MIB::ifName"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            ifindex = int(oid.split(".")[-1])
            if ifindex == 1 and ifname.startswith("Slot0/"):
                old_dlink = True
            if name and name != self.profile.convert_interface_name(ifname):
                continue
            if old_dlink:
                yield "name", ifindex, self.profile.convert_interface_name(ifname)
            if ifindex < 5121:
                continue
            ifnames[ifindex] = ifname
        if not old_dlink:
            for oid, ifname in self.snmp.getnext(
                mib["IF-MIB::ifDescr"],
                max_repetitions=self.get_max_repetitions(),
                max_retries=self.get_getnext_retires(),
            ):
                ifindex = int(oid.split(".")[-1])
                if name and name != self.profile.convert_interface_name(ifname):
                    continue
                if ifindex < 1024:  # physical interfaces
                    try:
                        v = self.profile.convert_interface_name(ifname)
                    except InterfaceTypeError as e:
                        self.logger.debug("Ignoring unknown interface %s: %s", ifname, e)
                        unknown_interfaces.append(ifname)
                        continue
                    yield "name", ifindex, self.profile.convert_interface_name(v)
                elif 5121 > ifindex >= 1024:  # 802.1q vlans
                    continue
                elif ifindex >= 5121:  # L3 interfaces
                    yield "name", ifindex, self.profile.convert_interface_name(ifnames[ifindex])
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored", len(unknown_interfaces))
