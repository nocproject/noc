# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MES24xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.validators import is_int


class Profile(BaseProfile):
    name = "Eltex.MES24xx"

    pattern_more = [(rb"--More--", b" ")]
    pattern_prompt = rb"(?P<hostname>\S+)(?:\(config[^\)]*\))?#\s*"
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>\s*"
    pattern_syntax_error = rb"^% Invalid (?:Command|input detected at)$"
    pattern_operation_error = rb"File Transfer in Progress"
    # command_disable_pager = "set cli pagination off"  - need conf t mode
    command_submit = b"\r"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    rogue_chars = [
        re.compile(rb"\s*\x1b\[27m"),
        re.compile(rb"\x1b\r\s+\r\x1b\[K"),
        re.compile(rb"\x1b\[K"),
        re.compile(rb"\r"),
        re.compile(rb"\x00."),
    ]

    config_normalizer = "MES24xxNormalizer"

    config_tokenizer = "indent"
    config_tokenizer_settings = {
        "end_of_context": "!",
        "string_quote": '"',
        # "rewrite": [(re.compile(r"^\s*(interface\s\w+)\s(\d+(\/\d+)*)$"), r"\1\2")],
    }
    confdb_defaults = [
        ("hints", "interfaces", "defaults", "admin-status", False),
    ]

    matchers = {
        "is_mes14_24": {"platform": {"$regex": "MES-?[12]4.."}},
    }

    # snmp_rate_limit = {"is_mes14_24": 4}

    INTERFACE_TYPES = {
        "te": "physical",  # tengigabitethernet
        "gi": "physical",  # gigabitethernet
        "fa": "physical",  # fastethernet
        "ex": "physical",  # extreme-ethernet
        "po": "aggregated",  # Port-channel/Portgroup
        "vl": "SVI",  # vlan
    }

    # Regex for join description when placed to 2 line when over 128 symbol
    # interface XXXX
    #   description "xxxxxxxxxxxxxxxxxxx
    # xx"
    rx_iface_over_description = re.compile(r"^(\s+description \".+)\n(\S.+)", re.MULTILINE)

    def cleaned_config(self, cfg):
        r = super().cleaned_config(cfg)
        if self.rx_iface_over_description.search(cfg):
            r = self.rx_iface_over_description.sub(r"\1\2", r)
        return r.strip()

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())

    # Eltex-like translation
    rx_eltex_interface_name = re.compile(
        r"^(?P<type>te|gi|fa|ex|po|vl)[a-z\-]*\s*"
        r"(?P<number>\d+(/\d+(/\d+)?)?(\.\d+(/\d+)*(\.\d+)?)?(:\d+(\.\d+)*)?"
        r"(/[a-z]+\d+(\.\d+)?)?(A|B)?)?",
        re.IGNORECASE,
    )

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name_cisco("gi1/0/1")
        'Gi 1/0/1'
        >>> Profile().convert_interface_name_cisco("gi1/0/1?")
        'Gi 1/0/1'
        """
        if s.startswith("Slot"):
            # @todo InterfaceType check needed
            s = s.replace("Slot", "gigabitethernet")
        match = self.rx_eltex_interface_name.match(str(s))
        if is_int(s):
            return "Vl %s" % s
        if s in ["oob", "stack-port"]:
            return s
        if match:
            return "%s %s" % (match.group("type").capitalize(), match.group("number"))
        raise InterfaceTypeError("Invalid interface '%s'" % s)
