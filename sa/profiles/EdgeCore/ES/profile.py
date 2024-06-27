# ---------------------------------------------------------------------
# Vendor: EdgeCore
# OS:     ES
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "EdgeCore.ES"

    pattern_unprivileged_prompt = rb"^(?P<hostname>[^\n]+)>"
    pattern_syntax_error = rb"% Invalid input detected at|% Incomplete command"
    command_super = b"enable"
    pattern_prompt = rb"^(?P<hostname>[^\n]+)(?:\(config[^)]*\))?#"
    pattern_more = [
        (rb"---?More---?", b" "),
        (rb"--- \[Space\] Next page, \[Enter\] Next line, \[A\] All, Others to exit ---", b" "),
        (rb"Are you sure to delete non-active file", b"Y\n\n"),
        (rb"Startup configuration file name", b"\n\n\n"),
    ]
    config_volatile = ["\x08+"]
    rogue_chars = [b"\r"]
    command_submit = b"\r"
    cli_timeout_prompt = 120
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    convert_mac = BaseProfile.convert_mac_to_dashed
    config_tokenizer = "indent"
    config_tokenizer_settings = {
        "line_comment": "!",
        "rewrite": [(re.compile("^queue mode"), " queue mode")],
    }
    config_normalizer = "ESNormalizer"
    confdb_defaults = [
        ("hints", "interfaces", "defaults", "admin-status", True),
        ("hints", "protocols", "lldp", "status", True),
        ("hints", "protocols", "spanning-tree", "status", False),
        ("hints", "protocols", "spanning-tree", "priority", "32768"),
        ("hints", "protocols", "loop-detect", "status", True),
        ("hints", "protocols", "ntp", "mode", "server"),
        ("hints", "protocols", "ntp", "version", "3"),
    ]
    matchers = {
        "is_platform_46": {"platform": {"$regex": r"46"}},
        "is_platform_4612": {"platform": {"$regex": r"4612"}},
        "is_platform_4626": {"platform": {"$regex": r"4626"}},
        "is_platform_ecs3510": {"platform": {"$regex": r"ECS3510"}},
        "is_platform_3510": {"platform": {"$regex": r"3510|3526|3528|3552|2228N|ECS4210|ECS4510"}},
        "is_platform_3510ma": {"platform": {"$regex": r"3510MA|ECS4210|ECS4510"}},
        "is_platform_3526s": {"platform": {"$regex": r"3526S"}},
        "is_platform_3528mv2": {"platform": {"$regex": r"3528MV2"}},
        "is_platform_ecs4100": {"platform": {"$regex": r"ECS4100"}},
    }
    rx_if_snmp_eth = re.compile(
        r"^Ethernet Port on Unit (?P<unit>\d+), port (?P<port>\d+)$", re.IGNORECASE
    )

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Eth 1/ 1")
        'Eth 1/1'
        >>> Profile().convert_interface_name("Ethernet Port on unit 1, port 21")
        'Eth 1/21'
        >>> Profile().convert_interface_name("Port12")
        'Eth 1/12'
        >>> Profile().convert_interface_name("ethernet 1/1")
        'Eth 1/1'
        """
        s = s.strip()
        if s.startswith("Port"):
            return "Eth 1/%s" % s[4:].strip()
        if s.startswith("ethernet "):
            return "Eth %s" % s[9:].strip()
        match = self.rx_if_snmp_eth.match(s)
        if match:
            return "Eth %s/%s" % (match.group("unit"), match.group("port"))
        s = s.replace("  ", " ")
        return s.replace("/ ", "/")

    def setup_session(self, script):
        try:
            script.cli("terminal length 0")
        except script.CLISyntaxError:
            pass

    @staticmethod
    def parse_ifaces(e=""):
        # Parse display interfaces output command for Huawei
        r = defaultdict(dict)
        current_iface = ""
        for line in e.splitlines():
            if not line or "===" in line:
                continue
            line = line.strip()
            if (
                line.startswith("LoopBack")
                or line.startswith("MEth")
                or line.startswith("Ethernet")
                or line.startswith("GigabitEthernet")
                or line.startswith("XGigabitEthernet")
                or line.startswith("Vlanif")
                or line.startswith("NULL")
            ):
                current_iface = line
                continue
            v, k = line.split(" ", 1)
            r[current_iface][k.strip()] = v.strip()
        return r

    INTERFACE_TYPES = {"eth": "physical", "vla": "SVI", "tru": "aggregated"}

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:3].lower(), "unknown")
