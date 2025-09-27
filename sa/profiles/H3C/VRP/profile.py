# ---------------------------------------------------------------------
# Vendor: H3C
# OS:     VRP
# Compatible: 3.1
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "H3C.VRP"

    pattern_more = [(rb"^  ---- More ----", b" ")]
    pattern_prompt = rb"^[<#]\S+?[>#]"
    config_volatile = [r"^%.*?$"]
    command_disable_pager = ""
    pattern_syntax_error = rb"% Wrong parameter|% Unrecognized command found at"

    matchers = {
        "is_old_version": {"version": {"$regex": r"3\.02.*"}},
        "is_310_version": {"version": {"$regex": r"3\.10.*"}},
        "is_3x_version": {"version": {"$regex": r"3\..*"}},
        "is_52_version": {"version": {"$regex": r"5\.2\S+"}},
        "is_53_version": {"version": {"$regex": r"5\.3\S+"}},
        "is_S3600_platform": {"platform": {"$regex": r".*S3600.*"}},
    }

    def generate_prefix_list(self, name, pl, strict=True):
        p = "ip ip-prefix %s permit %%s" % name
        if not strict:
            p += " le 32"
        return "undo ip ip-prefix %s\n" % name + "\n".join([p % x.replace("/", " ") for x in pl])

    rx_interface_name = re.compile(r"^(?P<type>Eth|[A-Z]+E|Vlan)(?P<number>[\d/]+)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        """
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        return "%s%s" % (
            {"GE": "GigabitEthernet", "Eth": "Ethernet", "Vlan": "Vlan-interface"}[
                match.group("type")
            ],
            match.group("number"),
        )

    convert_mac = BaseProfile.convert_mac_to_huawei

    spaces_rx = re.compile(r"^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

    def clean_spaces(self, config):
        return self.spaces_rx.sub("", config)
