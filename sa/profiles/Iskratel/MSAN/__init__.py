# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     MSAN
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.MSAN"
    pattern_username = "([Uu]ser ?[Nn]ame|[Ll]ogin)|User: ?"
    # Iskratel do not have "enable_super" command
    # pattern_unprivileged_prompt = r"^\S+?>"
    pattern_prompt = \
        r"^(\S+?|\(ISKRATEL Switching\)|Iskratel switching)\s*[#>]"
    pattern_more = [
        (r"Press any key to continue or ESC to stop scrolling.", " "),
        (r"Press any key to continue, ESC to stop scrolling or TAB to scroll to the end.", "\t"),
        (r"--More-- or \(q\)uit", " ")
    ]
    pattern_syntax_error = r"% Invalid input detected at|Command not found"
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    command_submit = "\r"
    # Iskratel SGR Not clearing command line when SyntaxError
    send_on_syntax_error = "\x1b[B"
    rogue_chars = ["\r", "\x00"]

    rx_hw = re.compile(
        r"System Description\.+ ISKRATEL Switching\n"
        r"Current CPU (?:Load|Usage)\.+ \d+%\n"
        r"Board Type\.+ (?P<platform>\S+)\n"
        r"Burned In MAC Address\.+ (?P<mac>\S+)\n"
        r"Board Serial Number\.+ (?P<serial>\S+)\n"
        r"Board Part Number\.+ (?P<part_no>\S+)\n"
        r"My board Position\.+ (?P<number>\S+)\n"
        r"IPMI version\.+ (?P<ipmi_ver>\S+)\n"
        r"Puma API Version\.+ (?P<api_ver>\S+)\n"
        r"Puma Microcode Version\.+ (?P<micr_ver>\S+)\n",
        re.MULTILINE)
    rx_hw2 = re.compile(
        r"System Description\.+ ISKRATEL Switching\n"
        r"Machine Type\.+ (?P<descr>.+)\n"
        r"Machine Model\.+ (?P<platform>.+)\n"
        r"Serial Number\.+ (?P<serial>\S+)\n"
        r"FRU Number\.+ (?P<number>\S*)\n"
        r"Part Number\.+ (?P<part_no>\S+)\n"
        r"Maintenance Level\.+ .+\n"
        r"Manufacturer\.+ .+\n"
        r"Burned In MAC Address\.+ (?P<mac>\S+)\n"
        r"(Operating System\.+ \S+\n)?"
        r"Network Processing Device\.+ .+\n.*"
        r"(Firmware Version\.+ (?P<api_ver>\S+)\n)?"
        r"Hardware( and CPLD)? Version\.+ (?P<hw_ver>\S+)\n.*"
        r"IPMI Version\.+ (?P<ipmi_ver>\S+)",
        re.MULTILINE | re.DOTALL)

    def get_hardware(self, script):
        c = script.cli("show hardware", cached=True)
        match = self.rx_hw.search(c)
        if match:
            return match.groupdict()
        else:
            match = self.rx_hw2.search(c)
            return match.groupdict()
