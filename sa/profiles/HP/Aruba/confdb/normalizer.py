# ----------------------------------------------------------------------
# HP.Aruba config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST, deferable
from noc.core.text import ranges_to_list

rx_multi_split = re.compile(r"\d+([km])")


class ArubaOSNormalizer(BaseNormalizer):
    @match("hostname", REST)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(" ".join(tokens[1:]))

    @match("vlan", ANY)
    def normalize_vlan(self, tokens):
        if tokens[1] != "database":
            for vid in ranges_to_list(tokens[1]):
                yield self.make_vlan_id(vlan_id=vid)

    @match("vlan", ANY, "name", REST)
    def normalize_vlan_name(self, tokens):
        yield self.make_vlan_name(vlan_id=tokens[1], name=" ".join(tokens[3:]))

    @match("interface", ANY)
    def normalize_interface_name(self, tokens):
        if "." in tokens[1]:
            pass
        #     ifname, unit = tokens[1].split(".")
        #     yield self.make_unit_description(
        #         interface=self.interface_name(ifname),
        #         unit=self.interface_name(tokens[1]),
        #         description="",
        #     )
        else:
            yield self.make_interface(interface=self.interface_name(tokens[1]))

    @match("interface", ANY, "shutdown")
    def normalize_interface_status(self, tokens):
        if "." not in tokens[1]:
            yield self.make_interface_admin_status(
                interface=self.interface_name(tokens[1]), admin_status=False
            )

    @match("interface", ANY, "mtu", ANY)
    def normalize_interface_mtu(self, tokens):
        yield self.make_interface_mtu(interface=self.interface_name(tokens[1]), mtu=tokens[3])

    @match("interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        if "." in tokens[1]:
            # ifname, unit = tokens[1].split(".")
            # yield self.make_unit_description(
            #     interface=self.interface_name(ifname),
            #     unit=self.interface_name(tokens[1]),
            #     description=" ".join(tokens[3:]),
            # )
            if_name = self.interface_name(tokens[1])
            yield self.defer(
                "fi.iface.%s" % if_name,
                self.make_unit_description,
                instance=deferable("instance"),
                interface=if_name,
                unit=self.interface_name(tokens[1]),
                description=" ".join(tokens[5:]),
            )
        else:
            yield self.make_interface_description(
                interface=self.interface_name(tokens[1]), description=" ".join(tokens[3:])
            )
