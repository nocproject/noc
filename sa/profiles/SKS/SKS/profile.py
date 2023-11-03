# ---------------------------------------------------------------------
# Vendor: SKS (SVYAZKOMPLEKTSERVICE, LLC. - https://www.nposkss.ru)
# OS:     SKS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "SKS.SKS"

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)\s*>"
    pattern_prompt = rb"^(?P<hostname>(?!#+)\S+)(?:\(e1\))?(?:_config\S*)?#"
    pattern_syntax_error = (
        rb"% Unrecognized command|% Wrong number of parameters|"
        rb"% Unrecognized host or address|"
        rb"Unknown command|Incomplete command|Too many parameters"
    )
    pattern_operation_error = (
        rb"%LCLI-W-E1MESSAGE: E1 units are not yet updated, cannot show running config."
    )
    command_super = b"enable"
    command_disable_pager = "terminal datadump"
    rogue_chars = [re.compile(rb"\r\n##+#\r\n"), b"\r"]
    pattern_more = [
        (rb"More: <space>,  Quit: q or CTRL+Z, One line: <return>", b"a"),
        (rb"^ --More-- ", b" "),
    ]
    config_volatile = [
        r"enable password 7 \S+( level \d+)?\n",
        r"username \S+ password 7 \S+( author\-group \S+)?\n",
        r"radius(-server | accounting-server )(encrypt-key|key) \d+ \S+\n",
        r"tacacs(-server | accounting-server )(encrypt-key|key) \d+ \S+\n",
    ]
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}

    matchers = {"is_sks_achtung": {"version": {"$regex": r"^2(\.\d+)+\w"}}}
    # 2.2.0C, 2.0.2H

    rx_iface_format = re.compile(r"^(?P<type>[a-zA-Z\-]*)(?P<number>\d+(?:\/\d+)*)$")

    iface_type_map = {
        "g": "GigaEthernet",
        "gi": "GigabitEthernet",
        "gig": "GigaEthernet",  # 2.0.2H, 2.0.2C from LLDP neighbors
        "gigabitethernet": "GigabitEthernet",
        "tg": "TGigaEthernet",
        "te": "TenGigabitEthernet",
        "tengigabitethernet": "TenGigabitEthernet",
        "v": "Vlan",
        "VLAN": "Vlan",
        "n": "Null",
        "t": "Tunnle",
        "tu": "Tunnel",
        "p": "Port-aggregator1",
        "po": "Port-Channel",
    }

    def convert_interface_name(self, interface):
        """
        For FW 2.0.2H/2.2.0C:
        GigaEthernet1/1 - g1/1
        TGigaEthernet1/1 - tg1/1
        Vlan1 - v1
        Null0 - n0
        Port-aggregator1 - p1
        For other
        GigabitEthernet1/1/1 - gi1/1/1
        TenGigabitEthernet1/1/2 - te1/1/2
        tengigabitethernet1/1/2 - TenGigabitEthernet1/1/2
        Port-Channel1 - Po1
        1 - Vlan1
        :param interface:
        :return:
        """
        if not self.rx_iface_format.match(interface):
            return interface
        iftype, ifnum = self.rx_iface_format.match(interface).groups()
        if not iftype:
            # VLAN on SNMP
            ifname = "Vlan%s" % ifnum
        elif iftype.lower() in self.iface_type_map:
            ifname = "%s%s" % (self.iface_type_map[iftype.lower()], ifnum)
        else:
            ifname = interface
        return ifname

    def setup_session(self, script):
        # additional command to `terminal datadump`
        script.cli("terminal length 0", ignore_errors=True)

    class e1(object):
        """E1 context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter e1 context"""
            self.script.cli("e1")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave e1 context"""
            if exc_type is None:
                self.script.cli("end")

    INTERFACE_TYPES = {
        "fa": "physical",  # FastEthernet
        "gi": "physical",  # GigabitEthernet
        "te": "physical",  # TenGigabitEthernet
        "tg": "physical",  # TenGigabitEthernet
        "po": "aggregated",  # Port-Channel
        "vl": "SVI",  # vlan
        "nu": "null",  # Null
    }

    @classmethod
    def get_interface_type(cls, name):
        if name.isdigit():
            # Vlan on SNMP
            return "SVI"
        return cls.INTERFACE_TYPES.get(name[:2].lower())

    rx_e1 = re.compile(r"e1 unit-1|!|config-file-header")
    rx_snmp = re.compile(r"snmp-server community 7 (\w+) ")

    def cleaned_config(self, cfg):
        cfg = super().cleaned_config(cfg)
        search = self.rx_e1.search(cfg)
        if search:
            cfg = cfg[search.span()[0] :]
        # SKS-16E1-IP-ES-L
        cfg = self.rx_snmp.sub("snmp-server community 7 XXXXX ", cfg)
        return cfg
