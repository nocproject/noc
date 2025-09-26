# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     MSAN
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.MSAN"

    pattern_username = b"([Uu]ser ?[Nn]ame|[Ll]ogin)|User: ?"
    # Iskratel do not have "enable_super" command
    pattern_unprivileged_prompt = rb"^(\S+?|\(ISKRATEL Switching\)|Iskratel switching)\s*>"
    pattern_prompt = rb"^(\S+?|\(ISKRATEL Switching\)|Iskratel switching)\s*(\(Config\))?#"
    pattern_more = [
        (rb"Press any key to continue or ESC to stop scrolling.", b" "),
        (rb"Press any key to continue, ESC to stop scrolling or TAB to scroll to the end.", b"\t"),
        (rb"Are you sure you want to save\? \(y/n\)", b"y"),
        (rb"--More-- or \(q\)uit", b" "),
    ]
    pattern_syntax_error = rb"% Invalid input detected at|Command not found"
    pattern_operation_error = rb"Error: RPC service is failed."
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    command_submit = b"\r"
    command_super = b"enable"
    password_submit = b"\r"
    username_submit = b"\r"
    # Iskratel SGR Not clearing command line when SyntaxError
    send_on_syntax_error = b"\x1b[B"
    rogue_chars = [b"\r", b"\x00"]

    matchers = {"is_switch_board": {"platform": {"$regex": r".*Switch.*"}}}

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
        re.MULTILINE,
    )
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
        re.MULTILINE | re.DOTALL,
    )

    def get_hardware(self, script):
        c = script.cli("show hardware", cached=True)
        match = self.rx_hw.search(c)
        if match:
            return match.groupdict()
        match = self.rx_hw2.search(c)
        return match.groupdict()

    rx_iface = re.compile(r"[01]/\d+")

    @classmethod
    def get_interface_type(cls, name):
        if cls.rx_iface.match(name):
            return "physical"
        if name == "2/1":
            return "aggregated"
        return "other"
