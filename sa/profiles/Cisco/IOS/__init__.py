# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     IOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Cisco.IOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = [
        (r"^ --More--", "\n"),
        (r"(?:\?|interfaces)\s*\[confirm\]", "\n")
    ]
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9/.]\S{0,35})(?:[-_\d\w]+)?(?:\(config[^\)]*\))?#"
    can_strip_hostname_to = 20
    requires_netmask_conversion = True
    convert_mac = NOCProfile.convert_mac_to_cisco
    config_volatile = ["^ntp clock-period .*?^"]

    rx_cable_if = re.compile(r"Cable\s*(?P<pr_if>\d+/\d+) U(pstream)?\s*(?P<sub_if>\d+)", re.IGNORECASE)
    default_parser = "noc.cm.parsers.Cisco.IOS.base.BaseIOSParser"

    def convert_interface_name(self, interface):
        if " efp_id " in interface:
            l, r = interface.split(" efp_id ", 1)
            return "%s.SI.%d" % (
                self.convert_interface_name_cisco(l.strip()),
                int(r.strip())
            )
        if "+Efp" in interface:
            l, r = interface.split("+Efp", 1)
            return "%s.SI.%d" % (
                self.convert_interface_name_cisco(l.strip()),
                int(r.strip())
            )
        if ".ServiceInstance." in interface:
            interface = interface.replace(".ServiceInstance.", ".SI.")
        if ".SI." in interface:
            l, r = interface.split(".SI.", 1)
            return "%s.SI.%d" % (
                self.convert_interface_name_cisco(l.strip()),
                int(r.strip())
            )
        if interface.startswith("NDE_"):
            return interface
        il = interface.lower()
        if il.startswith("dot11radio"):
            return "Dot11Radio" + interface[10:]
        if il.startswith("bdi"):
            return "BDI" + interface[3:]
        if il.startswith("bvi"):
            return "BVI" + interface[3:]
        if il.startswith("e1"):
            return "E1 %s" % interface[2:].strip()
        if il.startswith("t1"):
            return "T1 %s" % interface[2:].strip()
        if il.startswith("fxo null"):
            return "FXO %s" % interface[8:].strip()
        if il.startswith("fxs"):
            return "FXS %s" % interface[3:].strip()
        if il.startswith("efxs"):
            return "EFXS %s" % interface[4:].strip()
        if il.startswith("cpp"):
            return "CPP"
        if il.startswith("srp"):
            return "SRP %s" % interface[3:].strip()
        if il.startswith("Foreign Exchange Station"):
            return "FXS %s" % interface[24:].strip()
        if il.startswith("cable"):
            match = self.rx_cable_if.search(interface)
            if match:
                return "Ca %s/%s" % (match.group('pr_if'), match.group('sub_if'))
        if il.startswith("virtual-template"):
            return "Vi %s" % il[16:].strip()
        # Fake name. Used only with FM
        if il == "all":
            return "all"
        return self.convert_interface_name_cisco(interface)

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = "ip prefix-list %s permit %%s" % name
        mne = "ip prefix-list %s permit %%s le %%d" % name
        r = ["no ip prefix-list %s" % name]
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % prefix]
            else:
                r += [mne % (prefix, max_len)]
        return "\n".join(r)

    def setup_session(self, script):
        """
        Perform session initialization
        Process specific path parameters:
        cluster:id - switch to cluster member
        """
        cluster_member = None
        # Parse path parameters
        for p in script.access_profile.path.split("/"):
            if p.startswith("cluster:"):
                cluster_member = p[8:].strip()
        # Switch to cluster member, if necessary
        if cluster_member:
            script.debug("Switching to cluster member '%s'" % cluster_member)
            script.cli("rc %s" % cluster_member)

    INTERFACE_TYPES = {
        "As": "physical",  # Async
        "AT": "physical",  # ATM
        "At": "physical",  # ATM
        "Br": "physical",  # ISDN Basic Rate Interface
        "BD": "physical",  # Bridge Domain Interface
        "BV": "aggregated",  # BVI
        "Bu": "aggregated",  # Bundle
        "C": "physical",  # @todo: fix
        "Ca": "physical",  # Cable
        "CD": "physical",  # CDMA Ix
        "Ce": "physical",  # Cellular
        "Em": "physical",  # Embedded Service Engine
        "Et": "physical",  # Ethernet
        "Fa": "physical",  # FastEthernet
        "Fd": "physical",  # Fddi
        "Gi": "physical",  # GigabitEthernet
        "Gm": "physical",  # GMPLS
        "Gr": "physical",  # Group-Async
        "Lo": "loopback",  # Loopback
        "In": "physical",  # Integrated-service-engine
        "M": "management",  # @todo: fix
        "MF": "aggregated",  # Multilink Frame Relay
        "Mf": "aggregated",  # Multilink Frame Relay
        "Mu": "aggregated",  # Multilink-group interface
        "PO": "physical",  # Packet OC-3 Port Adapter
        "Po": "aggregated",  # Port-channel/Portgroup
        "R": "aggregated",  # @todo: fix
        "SR": "physical",  # Spatial Reuse Protocol
        "Sr": "physical",  # Spatial Reuse Protocol
        "Se": "physical",  # Serial
        "Sp": "physical",  # Special-Services-Engine
        "Te": "physical",  # TenGigabitEthernet
        "To": "physical",  # TokenRing
        "Tu": "tunnel",  # Tunnel
        "Vi": "template", # Virtual-Template
        "VL": "SVI",  # VLAN, found on C3500XL
        "Vl": "SVI",  # Vlan
        "Vo": "physical",  # Voice
        "XT": "SVI"  # Extended Tag ATM
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])


def uBR(v):
    """
    uBR series selector
    """
    return "BC" in v["version"]


def MESeries(v):
    """
    MExxxx series selector
    :param v:
    :type v: dict
    :return:
    :rtype: bool
    """
    return v["platform"].startswith("ME")
