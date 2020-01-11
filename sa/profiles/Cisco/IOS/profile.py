# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     IOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import six

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.IOS"
    pattern_more = [
        (r"^ --More-- ", " "),
        (r"(?:\?|interfaces)\s*\[confirm\]", "\n"),
        (r"^Destination filename \[\S+\]", "\n"),
        (r"^Proceed with reload\?\s*\[confirm\]", "y\n"),
    ]
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    pattern_operation_error = "Command authorization failed."
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9/.]\S{0,35})(?:[-_\d\w]+)?(?:\(config[^\)]*\))?#"
    can_strip_hostname_to = 20
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
    config_volatile = ["^ntp clock-period .*?^"]

    rx_cable_if = re.compile(
        r"Cable\s*(?P<pr_if>\d+/\d+) U(pstream)?\s*(?P<sub_if>\d+)", re.IGNORECASE
    )
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}
    config_normalizer = "CiscoIOSNormalizer"
    confdb_defaults = [
        ("hints", "interfaces", "defaults", "admin-status", True),
        ("hints", "protocols", "lldp", "status", False),
        ("hints", "protocols", "cdp", "status", True),
        ("hints", "protocols", "ntp", "mode", "server"),
        ("hints", "protocols", "ntp", "version", "3"),
        # ("hints", "protocols", "loop-detect", "status", False),
    ]
    default_parser = "noc.cm.parsers.Cisco.IOS.base.BaseIOSParser"
    rx_ver = re.compile(r"(\d+)\.(\d+)[\(.](\d+)[\).]\S*")

    matchers = {
        "is_platform_7200": {"platform": {"$regex": r"720[0146]|730[14]"}},
        "is_platform_7600": {"platform": {"$regex": r"76(0[3459](\-S)?|13)"}},
        "is_platform_me3x00x": {"platform": {"$regex": r"^ME\-3[68]00X"}},
        "is_isr_router": {"platform": {"$regex": r"^(19\d\d|29\d\d|39\d\d)$"}},
        "is_iosxe": {"platform": {"$regex": r"ASR100[0-6]"}},
        "is_cat6000": {"version": {"$regex": r"S[YXR]"}},
        "is_cat4000": {"platform": {"$regex": r"^WS-C4[059]\d\d"}},
        "is_small_cat": {"version": {"$regex": r"SE|EA|EZ|FX|EX|EY|E|WC"}},
        "is_5350": {"platform": {"$regex": r"^5350"}},
        "is_ubr": {"version": {"$regex": r"BC"}},
        "is_vlan_switch": {
            "platform": {
                "$regex": r"^([123][678]\d\d|7[235]\d\d|107\d\d|"
                r"C[23][69]00[a-z]?$|C8[7859]0|17\d\d|C18[01]X|19\d\d|2951|ASR\d+)"
            }
        },
    }

    def cmp_version(self, x, y):
        """12(25)SEC2"""
        a = [int(z) for z in self.rx_ver.findall(x)[0]]
        b = [int(z) for z in self.rx_ver.findall(y)[0]]
        return (a > b) - (a < b)

    def convert_interface_name(self, interface):
        interface = str(interface)
        if " efp_id " in interface:
            l, r = interface.split(" efp_id ", 1)
            return "%s.SI.%d" % (self.convert_interface_name_cisco(l.strip()), int(r.strip()))
        if "+Efp" in interface:
            l, r = interface.split("+Efp", 1)
            return "%s.SI.%d" % (self.convert_interface_name_cisco(l.strip()), int(r.strip()))
        if " point-to-point" in interface:
            interface = interface.replace(" point-to-point", "")
        if ".ServiceInstance." in interface:
            interface = interface.replace(".ServiceInstance.", ".SI.")
        if ".SI." in interface:
            l, r = interface.split(".SI.", 1)
            return "%s.SI.%d" % (self.convert_interface_name_cisco(l.strip()), int(r.strip()))
        if isinstance(interface, six.string_types):
            il = interface.lower()
        else:
            il = interface.name.lower()
        if il.startswith("nde_"):
            return "NDE_" + interface[4:]
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
                return "Ca %s/%s" % (match.group("pr_if"), match.group("sub_if"))
        if il.endswith(" type tunnel"):
            il = il[:-12]
        if il.startswith("virtual-template"):
            return "Vi %s" % il[16:].strip()
        if il.startswith("service-engine"):
            return "Service-Engine %s" % il[14:].strip()
        # Serial0/1/0:15-Signaling -> Serial0/1/0:15
        if il.startswith("se") and "-" in interface:
            interface = interface.split("-")[0]
        # Control Plane Interface
        # @todo: Does it relates to CPP?
        if il == "control plane interface":
            return "Control Plane Interface"
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
        path = script.credentials.get("path")
        if path:
            cluster_member = None
            # Parse path parameters
            for p in script.credentials.get("path", "").split("/"):
                if p.startswith("cluster:"):
                    cluster_member = p[8:].strip()
            # Switch to cluster member, if necessary
            if cluster_member:
                script.logger.debug("Switching to cluster member '%s'" % cluster_member)
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
        "Fo": "physical",  # FortyGigabitEthernet
        "Gi": "physical",  # GigabitEthernet
        "Gm": "physical",  # GMPLS
        "Gr": "physical",  # Group-Async
        "Lo": "loopback",  # Loopback
        "In": "physical",  # Integrated-service-engine
        "M": "management",  # @todo: fix
        "MF": "aggregated",  # Multilink Frame Relay
        "Mf": "aggregated",  # Multilink Frame Relay
        "Mu": "aggregated",  # Multilink-group interface
        "ND": "other",  # Netflow Data Exporter
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
        "Vi": "template",  # Virtual-Template
        "VL": "SVI",  # VLAN, found on C3500XL
        "Vl": "SVI",  # Vlan
        "Vo": "physical",  # Voice
        "XT": "SVI",  # Extended Tag ATM
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
