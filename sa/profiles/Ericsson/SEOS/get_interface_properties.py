# ----------------------------------------------------------------------
# Ericsson.SEOS.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Ericsson.SEOS.get_interface_properties"

    MAX_GETNEXT_RETIRES = 0

    def iter_interface_ifindex(self, name: str):
        d = {}
        unknown_interfaces = []
        ifaces = set()

        for doid, descr in self.snmp.getnext(
            mib["IF-MIB::ifDescr"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            dindex = int(doid.split(".")[-1])
            d[dindex] = descr
        for oid, ifname in self.snmp.getnext(
            mib["IF-MIB::ifName"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            ifindex = int(oid.split(".")[-1])
            if ifname in ifaces:
                ifname = "%s-%s" % (ifname, d[ifindex])
            ifaces.add(ifname)
            try:
                v = self.profile.convert_interface_name(ifname.strip())
            except InterfaceTypeError as e:
                self.logger.debug("Ignoring unknown interface %s: %s", ifname, e)
                unknown_interfaces += [ifname]
                continue
            if name and name != v:
                continue
            yield "name", ifindex, v
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored", len(unknown_interfaces))
