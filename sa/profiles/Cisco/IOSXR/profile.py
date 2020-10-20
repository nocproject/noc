# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     IOS XR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.sa.interfaces.base import InterfaceTypeError


class Profile(BaseProfile):
    name = "Cisco.IOSXR"
    pattern_more = r"^ --More--"
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_exit = "exit"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco

    rx_interface_name = re.compile(
        r"^(?P<type>[a-z\-]+)\s*(?P<number>\d+(?:/\d+)*(?:\.\d+)?(?:\.ip\d+)?(?:(?:/RS?P\d+)?/CPU\d+(?:/\d+)*)?)$",
        re.IGNORECASE,
    )

    matchers = {"is_platform_crs16": {"platform": {"$regex": r"CRS-16"}}}

    def convert_interface_name(self, s):
        """
        MgmtEth0/1/CPU0/0
        GigabitEthernet0/2/0/0.1000
        Te0/0/1/3
        Bundle-Ether1.5011035
        Bundle-Ether1.10231016.ip18484
        """
        match = self.rx_interface_name.match(s)
        if not match:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
        t = match.group(1)[:2]
        if t.lower() == "bu":
            t = "BE"
        return "%s%s" % (t, match.group(2))

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = " %s"
        mne = " %s le %d"
        r = []
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % prefix]
            else:
                r += [mne % (prefix, max_len)]
        return "\n".join(["prefix-set %s" % name, ",\n".join(r), "end-set"])

    INTERFACE_TYPES = {
        "As": "physical",  # Async
        "AT": "physical",  # ATM
        "At": "physical",  # ATM
        "Br": "physical",  # ISDN Basic Rate Interface
        "BD": "physical",  # Bridge Domain Interface
        "BV": "aggregated",  # BVI
        "BE": "aggregated",  # Bundle
        "Ca": "physical",  # Cable
        "CD": "physical",  # CDMA Ix
        "Ce": "physical",  # Cellular
        "Em": "physical",  # Embedded Service Engine
        "E1": "other",  # E1
        "Et": "physical",  # Ethernet
        "Fa": "physical",  # FastEthernet
        "Fd": "physical",  # Fddi
        "Fi": "physical",  # FiveGigabitEthernet
        "Fo": "physical",  # FortyGigabitEthernet
        "Gi": "physical",  # GigabitEthernet
        "Gm": "physical",  # GMPLS
        "Gr": "physical",  # Group-Async
        "Hu": "physical",  # HundredGigabitEthernet
        "Lo": "loopback",  # Loopback
        "In": "physical",  # Integrated-service-engine
        "Mg": "management",  # Management interface
        "MF": "aggregated",  # Multilink Frame Relay
        "Mf": "aggregated",  # Multilink Frame Relay
        "Mu": "aggregated",  # Multilink-group interface
        "ND": "other",  # Netflow Data Exporter
        "PO": "physical",  # Packet OC-3 Port Adapter
        "Po": "aggregated",  # Port-channel/Portgroup
        "SR": "physical",  # Spatial Reuse Protocol
        "Sr": "physical",  # Spatial Reuse Protocol
        "Se": "physical",  # Serial
        "Sp": "physical",  # Special-Services-Engine
        "St": "physical",  # StackSub-St, StackPort1
        "Te": "physical",  # TenGigabitEthernet
        "To": "physical",  # TokenRing
        "Tu": "tunnel",  # Tunnel
        "Tw": "physical",  # TwoGigabitEthernet or TwentyFiveGigE
        "Vi": "template",  # Virtual-Template
        "VL": "SVI",  # VLAN, found on C3500XL
        "Vl": "SVI",  # Vlan
        "Vo": "physical",  # Voice
        "XT": "SVI",  # Extended Tag ATM
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
