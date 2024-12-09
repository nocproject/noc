# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MES
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.validators import is_int
from noc.core.snmp.render import render_mac


class Profile(BaseProfile):
    name = "Eltex.MES"

    pattern_more = [
        (rb"^.*More: <space>,  Quit: q(\sor CTRL\+Z)?, One line: <return>.*$", b" "),
        (rb"\[Yes/press any key for no\]", b"Y"),
        (rb"<return>, Quit: q or <ctrl>", b" "),
        (rb"q or <ctrl>+z", b" "),
        (rb"Overwrite file \[startup-config\].... \(Y\/N\)", b"Y"),
        (rb"Would you like to continue \? \(Y\/N\)\[N\]", b"Y"),
        (rb"Clear Logging File \? \(Y\/N\)\[N\]", b"Y"),
        (rb"press ENTER key to retry authentication", b"\n"),
    ]
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>\s*"
    pattern_syntax_error = (
        rb"% (Unrecognized command|Incomplete command|"
        rb"Wrong number of parameters or invalid range, size or "
        rb"characters entered)"
    )
    pattern_operation_error = rb"command authorization failed"
    # command_disable_pager = "terminal datadump"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = rb"^(?P<hostname>[A-Za-z0-9-_ \:\.\*\'\,\(\)\/]+)?(?:\(config[^\)]*\))?#"
    rogue_chars = [re.compile(rb"\d+-\w+-\d+\s\d+:\d+:\d+\s\%\S+\:.+"), b"\r"]
    # to one SNMP GET request
    snmp_metrics_get_chunk = 10
    config_tokenizer = "indent"
    config_tokenizer_settings = {
        "line_comment": "!",
        "end_of_context": "exit",
        "rewrite": [(re.compile(r"^\s*(interface\s\w+)\s(\d+(\/\d+)*)$"), r"\1\2")],
    }
    config_normalizer = "MESNormalizer"
    confdb_defaults = [
        ("hints", "interfaces", "defaults", "admin-status", True),
        ("hints", "protocols", "lldp", "status", True),
        ("hints", "protocols", "spanning-tree", "status", False),
        ("hints", "protocols", "spanning-tree", "priority", "32768"),
        ("hints", "protocols", "loop-detect", "status", False),
        ("hints", "protocols", "ntp", "mode", "server"),
        ("hints", "protocols", "ntp", "version", "3"),
    ]

    matchers = {
        "is_has_image": {"image": {"$regex": r"^\S+"}},
        "is_has_chgroup": {
            "version": {"$regex": r"^([12]\.[15]\.4[4-9]|4\.0\.[1,2,5-9]|6\.[12,4]\.[12]|6\.5\.0)"}
        },
        "is_3124": {"platform": {"$regex": "3[13](24|48)"}},
    }

    snmp_display_hints = {"1.3.6.1.4.1.89.53.4.1.7.1": render_mac}

    PLATFORMS = {
        "24": "MES-3124",
        "26": "MES-5148",
        "30": "MES-3124F",
        "35": "MES-3108",
        "36": "MES-3108F",
        "38": "MES-3116",
        "39": "MES-3116F",
        "40": "MES-3224",
        "41": "MES-3224F",
        "42": "MES-1024",
        "43": "MES-2124",
        "52": "MES-1124",
        "54": "MES-5248",
        "58": "MES-2208P",
        "59": "MES-2124P",
        "74": "MES-5324",
        "75": "MES-2124F",
        "76": "MES-2324",
        "77": "MES-2324F",
        "78": "MES-2324FB",
        "80": "MES-3324",
        "81": "MES-3324F",
        "83": "MES-2324B",
        "86": "MES-2348B",
        "88": "MES-2308",
        "89": "MES-2308P",
        "92": "MES-2324P",
        "96": "MES-3348",
        "98": "MES-3508P",
        "112": "MES-2308R",
        "116": "MES-3308F",
        "117": "MES-3316F",
        "120": "MES-3348F",
        "136": "MES-5316A",
        "142": "MES-3348F",  # rev.B
        "190": "MES-3324F",  # rev.B
        "192": "MES-2324FB",
        "235": "MES-2348P",
    }

    def setup_session(self, script):
        try:
            script.cli("terminal datadump")
            script.cli("")  # "сommand authorization failed" - not syntax error
        except script.CLISyntaxError:
            pass

    REVISIONS = {"190": "rev.B"}

    def get_platform(self, s):
        return self.PLATFORMS.get(s), self.REVISIONS.get(s)

    INTERFACE_TYPES = {
        "as": "physical",  # Async
        "at": "physical",  # ATM
        "bv": "aggregated",  # BVI
        "bu": "aggregated",  # Bundle
        # "C": "physical",     # @todo: fix
        "ca": "physical",  # Cable
        "cd": "physical",  # CDMA Ix
        "ce": "physical",  # Cellular
        "et": "physical",  # Ethernet
        "fa": "physical",  # FastEthernet
        "gi": "physical",  # GigabitEthernet
        "te": "physical",  # TenGigabitEthernet
        "tw": "physical",  # TwentyFiveGigaEthernet
        "fo": "physical",  # FortyGigabitEthernet
        "hu": "physical",  # HundredGigabitEthernet
        "gr": "physical",  # Group-Async
        "lo": "loopback",  # Loopback
        "oo": "management",  # oob
        "mf": "aggregated",  # Multilink Frame Relay
        "mu": "aggregated",  # Multilink-group interface
        "po": "aggregated",  # Port-channel/Portgroup
        # "R": "aggregated",   # @todo: fix
        "sr": "physical",  # Spatial Reuse Protocol
        "se": "physical",  # Serial
        "st": "management",  # Stack-port
        "tu": "tunnel",  # Tunnel
        "vl": "SVI",  # VLAN, found on C3500XL
        "xt": "SVI",  # Extended Tag ATM
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())

    # Eltex-like translation
    rx_eltex_interface_name = re.compile(
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*"
        r"(?P<number>\d+(/\d+(/\d+)?)?(\.\d+(/\d+)*(\.\d+)?)?(:\d+(\.\d+)*)?(/[a-z]+\d+(\.\d+)?)?(A|B)?)?",
        re.IGNORECASE,
    )

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("gi1/0/1")
        'Gi 1/0/1'
        >>> Profile().convert_interface_name("gi1/0/1?")
        'Gi 1/0/1'
        >>> Profile().convert_interface_name("vlan 10")
        'Vl 10'
        """
        match = self.rx_eltex_interface_name.match(str(s))
        if is_int(s):
            return "Vl %s" % s
        elif s in ["oob", "stack-port"]:
            return s
        elif match:
            return "%s %s" % (match.group("type").capitalize(), match.group("number"))
        else:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
