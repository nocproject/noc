# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: EdgeCore
# OS:     ES
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "EdgeCore.ES"
    pattern_unprivileged_prompt = r"^(?P<hostname>[^\n]+)>"
=======
##----------------------------------------------------------------------
## Vendor: EdgeCore
## OS:     ES
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "EdgeCore.ES"
    supported_schemes = [TELNET, SSH]
    pattern_unpriveleged_prompt = r"^(?P<hostname>[^\n]+)>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"% Invalid input detected at|% Incomplete command"
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>[^\n]+)(?:\(config[^)]*\))?#"
    pattern_more = [
        (r"---?More---?", " "),
        (r"--- \[Space\] Next page, \[Enter\] Next line, \[A\] All, Others to exit ---", " "),
<<<<<<< HEAD
        (r"Are you sure to delete non-active file", "Y\n\n"),
        (r"Startup configuration file name", "\n\n\n")
=======
        (r"Startup configuration file name", "\n")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    ]
    config_volatile = ["\x08+"]
    rogue_chars = ["\r"]
    command_submit = "\r"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
<<<<<<< HEAD
    convert_mac = BaseProfile.convert_mac_to_dashed

    rx_if_snmp_eth = re.compile(
        r"^Ethernet Port on Unit (?P<unit>\d+), port (?P<port>\d+)$",
        re.IGNORECASE
    )
=======
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_dashed
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Eth 1/ 1")
        'Eth 1/1'
<<<<<<< HEAD
        >>> Profile().convert_interface_name("Ethernet Port on unit 1, port 21")
        'Eth 1/21'
        >>> Profile().convert_interface_name("Port12")
        'Eth 1/12'
        """
        s = s.strip()
        if s.startswith("Port"):
            return "Eth 1/%s" % s[4:].strip()
        match = self.rx_if_snmp_eth.match(s)
        if match:
            return "Eth %s/%s" % (match.group("unit"),
                                  match.group("port"))
=======
        """
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        s = s.replace("  ", " ")
        return s.replace("/ ", "/")

    def setup_session(self, script):
        try:
            script.cli("terminal length 0")
        except script.CLISyntaxError:
            pass
<<<<<<< HEAD

    @staticmethod
    def parse_ifaces(e=""):
        # Parse display interfaces output command for Huawei
        r = defaultdict(dict)
        current_iface = ""
        for line in e.splitlines():
            print line
            if not line or "===" in line:
                continue
            line = line.strip()
            if (line.startswith("LoopBack") or line.startswith("MEth") or
                    line.startswith("Ethernet") or
                    line.startswith("GigabitEthernet") or line.startswith("XGigabitEthernet") or
                    line.startswith("Vlanif") or line.startswith("NULL")):
                current_iface = line
                continue
            v, k = line.split(" ", 1)
            r[current_iface][k.strip()] = v.strip()
        return r
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
