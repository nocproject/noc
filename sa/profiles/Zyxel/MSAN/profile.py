# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     MSAN
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.MSAN"

    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9-_\(\)\.\' /]+?)(config|chips|bridge|ethernet|adsl|gshdsl|vlan1q)?[#>]\s*"
    pattern_syntax_error = rb"((Unknown|invalid) (command|input)|Commands are:)"
    pattern_more = [
        (rb"Press any key to continue, 'n' to nopause,'e' to exit", b"n"),
        (rb"Press any key to continue, 'e' to exit, 'n' for nopause", b"n"),
        (rb"Using command \"stop\" to terminate", b"stop"),
        (rb"continue...", b" "),
    ]
    config_volatile = [r"^time\s+(\d+|date).*?^"]

    snmp_metrics_get_chunk = 30
    snmp_metrics_get_timeout = 3
    snmp_ifstatus_get_chunk = 30
    snmp_ifstatus_get_timeout = 3

    enable_cli_session = False
    command_exit = "exit"

    def convert_interface_name(self, interface):
        if interface.startswith("enet"):
            return "Enet" + interface[4:]
        elif interface.startswith("adsl") or interface.startswith("vdsl"):
            return interface[4:]
        else:
            return interface

    def setup_session(self, script):
        # Useful only on IES-1000
        script.cli("home", ignore_errors=True)

    rx_slots = re.compile(r"slot number should between 1 to (?P<slot>\d+)")
    rx_slots2 = re.compile(r"slot id:\s*1 to (?P<slot>\d+)")

    def get_slots_n(self, script):
        try:
            slots = script.cli("lcman show 100", cached=True)
            if "slot id" in slots:
                # IES-2000
                match = self.rx_slots2.search(slots)
            else:
                match = self.rx_slots.search(slots)
            return int(match.group("slot"))
        except script.CLISyntaxError:
            return 1

    def get_platform(self, script, slot_no, hw):
        if slot_no == 5:
            if hw in ["MSC1000G"]:
                return "IES-5005"
        if slot_no == 6:
            if hw in ["MSC1024GB", "MSC1224GB"]:
                return "IES-5106M"
            if hw in ["MSC1000"]:
                return "IES-2000"
            if hw in ["MSC1000A"]:
                return "IES-2000M"
        if slot_no == 10:
            if hw in ["MSC1000G"]:
                return "IES-5000"
        if slot_no == 12:
            if hw in ["MSC1024GB", "MSC1224GB"]:
                return "IES-5112M"
        if slot_no == 6:
            if hw in ["MSC1000"]:
                return "IES-3000"
            if hw in ["MSC1000A"]:
                return "IES-3000M"
        if slot_no == 16:
            if hw in ["MSC1000"]:
                return "IES-3000"
        if slot_no == 17:
            if hw in ["MSC1024GB", "MSC1224GB", "MSC1024G", "MSC1224G"]:
                return "IES-6000"
        if slot_no == 1:
            if hw in ["IES1248-51", "IES1248-71"]:
                return "IES-1248"
            if hw == "AAM1212-51" or hw == "AAM1212-53":
                return "IES-1000"
            # Need more examples
            if hw == "IES-612":
                return "IES-612"
        return ""
