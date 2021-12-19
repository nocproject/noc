# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     MA5300
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.MA5300"

    pattern_more = [
        (rb"--- More:", b" "),
        (rb"[ ]+---- More \(Press CTRL\+C break\) ---[ ]+", b" "),  # [ ]+ use for save \n in output
        # stream, because more pattern remove from stream
        (rb"Note: Terminal", b"\n"),
        (rb"Warning: Battery is low power!", b"\n"),
        (rb"\{\s<cr>.*\s\}:", b"\n"),
        (rb"^Are you sure?\[Y/N\]", b"y\n"),
        (rb"^\{ terminal\<K\> \}\:", b"terminal\n"),
        (rb"\{ <cr>\|interface<K> \}\:", b"\n"),
    ]
    pattern_username = rb"^Username:"
    pattern_password = rb"^Password:"
    command_exit = "logout"
    command_super = b"enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_save_config = "save"
    enable_cli_session = False  # With False mixin commands output over script
    pattern_prompt = rb"(?P<hostname>\S+)(?:\(.*)?#"
    pattern_unprivileged_prompt = rb"^(?P<hostname>[a-zA-Z0-9-_\.\/()]+)(?:-[a-zA-Z0-9/]+)*>$"
    pattern_syntax_error = (
        rb"(% Unknown command, the error locates at \'^\'|  Logged Fail!|"
        rb"System is busy, please try after a while)"
    )
    rogue_chars = [
        re.compile(br"\x1b\[39D\s+\x1b\[39D"),
        re.compile(br"\n\r\s+Line \d+ operating, attempt of the Line -\d+ denied!\n\r"),
        re.compile(br"\r\n\s+Note: Terminal users login \(IP: \S+ \)"),
        re.compile(br"\r\nWarning: Battery is low power!"),
        b"\r",
    ]
    # to one SNMP GET request
    snmp_metrics_get_chunk = 30
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5
    # to one SNMP GET request for get_interface_status_ex
    snmp_ifstatus_get_chunk = 30
    # Timeout for snmp GET request for get_interface_status_ex
    snmp_ifstatus_get_timeout = 3

    _IF_TYPES = {
        "aux": "other",
        "loo": "loopback",
        "m-e": "management",
        "nul": "null",
        "vla": "SVI",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls._IF_TYPES.get(name[:3].lower(), "unknown")

    def get_interface_snmp_index(self, name):
        return None

    # def setup_session(self, script):
    #     script.cli("terminal type vt100", ignore_errors=True)
    #     script.cli("config", ignore_errors=True)
    #     script.cli("line vty 0 3", ignore_errors=True)
    #     script.cli("history size 0", ignore_errors=True)
    #     script.cli("length 0", ignore_errors=True)
    #     script.cli("exit", ignore_errors=True)
    #     script.cli("cls", ignore_errors=True)

    # def shutdown_session(self, script):
    #     script.cli("config", ignore_errors=True)
    #     script.cli("line vty 0 3", ignore_errors=True)
    #     script.cli("no length 0", ignore_errors=True)
    #     script.cli("exit", ignore_errors=True)
