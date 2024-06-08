# ---------------------------------------------------------------------
# Vendor: Raisecom
# OS:     ROS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from dateutil.parser import parse, ParserError

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.confdb.syntax.patterns import ANY


class Profile(BaseProfile):
    name = "Raisecom.ROS"
    pattern_unprivileged_prompt = rb"^\S+?>"
    command_super = b"enable"
    pattern_prompt = rb"^\S+?#"
    command_exit = "exit"
    pattern_more = [(rb"^ --More--\s*", b" ")]
    pattern_syntax_error = rb"(% \".+\"  (?:Unknown command.)|Error input in the position marke[dt] by|%\s+Incomplete command\.)"
    pattern_operation_error = rb"% You Need higher priority!"
    rogue_chars = [re.compile(rb"\x08+\s+\x08+"), b"\r"]
    config_volatile = [
        r"radius(-server | accounting-server |-)encrypt-key \S+\n",
        r"tacacs(-server | accounting-server |-)encrypt-key \S+\n",
    ]
    config_tokenizer = "context"
    config_tokenizer_settings = {
        "line_comment": "!",
        "contexts": [["interface", ANY, ANY]],
        "end_of_context": "!",
    }

    matchers = {
        "is_not_iscom2608g": {"platform": {"$regex": r"(?i)^(?!ISCOM26(?:08|24|48)G)"}},
        "is_iscom2624g": {"platform": {"$regex": r"ISCOM26(?:08|24|48)G"}},
        "is_iscom2924g": {"platform": {"$regex": r"ISCOM2924G"}},
        "is_rotek": {"vendor": {"$in": ["Rotek", "ROTEK"]}},
        "is_gazelle": {"platform": {"$regex": r"^[SR]\d+[Ii]\S+"}},
        "is_ifname_use": {"platform": {"$regex": "QSW-8200"}},
        "is_version_only_format": {
            "version": {"$regex": r"^\d+\S+"}
        },  # Version format 5.2.1_20171221
    }

    rx_date_format = re.compile(r"(\S+)\s*\((.+)\)")
    rx_path_version = re.compile(r"(\S+)\s*\((\S+)\)")

    @classmethod
    def cmp_version(cls, v1, v2):
        """
        Compare two versions.
        Default implementation compares a versions in format
        N1. .. .NM
        On Qtech.QSW2800
        """
        if not cls.rx_path_version.match(v1) and cls.rx_date_format.match(v1):
            v_part, d_part = cls.rx_date_format.match(v1).groups()
            try:
                d_part = parse(d_part)
                v1 = f"{v_part} {d_part.isoformat()}"
            except ParserError:
                pass
        if not cls.rx_path_version.match(v2) and cls.rx_date_format.match(v2):
            v_part, d_part = cls.rx_date_format.match(v2).groups()
            try:
                d_part = parse(d_part)
                v2 = f"{v_part} {d_part.isoformat()}"
            except ParserError:
                pass
        return super().cmp_version(v1, v2)

    rx_port = re.compile(r"^[Pp]ort(|\s+)(?P<port>\d+)")  # Port1-FastEthernet,port 1
    rx_port_ip = re.compile(r"^(IP|ip interface)(|\s+)(?P<port>\d+)")  # ip interface 0, IP0

    def convert_interface_name(self, interface):
        if interface.startswith("GE"):
            return interface.replace("GE", "gigaethernet")
        if interface.startswith("FE"):
            return interface.replace("FE", "fastethernet")
        if self.rx_port.match(interface):
            match = self.rx_port.match(interface)
            return match.group("port")
        if self.rx_port_ip.match(interface):
            match = self.rx_port_ip.match(interface)
            return "ip %s" % match.group("port")
        else:
            return interface

    INTERFACE_TYPES = {
        "nu": "null",  # NULL
        "fa": "physical",  # fastethernet
        "fe": "physical",  # fastethernet
        "gi": "physical",  # gigaethernet
        "ge": "physical",  # gigaethernet
        "lo": "loopback",  # Loopback
        "tr": "aggregated",  #
        "po": "aggregated",  # port-channel
        "mn": "management",  # Stack-port
        # "te": "physical",  # TenGigabitEthernet
        "vl": "SVI",  # vlan
        "ip": "SVI",  # IP interface
        "un": "unknown",
    }

    @classmethod
    def get_interface_type(cls, name):
        if name == "fastethernet1/0/1":
            # for ISCOM26(?:24|08)G
            # @todo use matchers
            return "management"
        elif name.isdigit():
            return "physical"
        return cls.INTERFACE_TYPES.get(name[:2].lower())
