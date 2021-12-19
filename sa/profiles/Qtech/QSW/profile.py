# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QSW
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.lldp import LLDP_PORT_SUBTYPE_COMPONENT, LLDP_PORT_SUBTYPE_NAME


class Profile(BaseProfile):
    name = "Qtech.QSW"

    pattern_username = rb"^(Username\(1-32 chars\)|[Ll]ogin):"
    pattern_password = rb"^Password(\(1-16 chars\)|):"
    pattern_more = [
        (
            rb"^\.\.\.\.press ENTER to next line, CTRL_C to break, other key "
            rb"to next page\.\.\.\.",
            b" ",
        ),
        (rb"^Startup config in flash will be updated, are you sure\(y/n\)\? \[n\]", b"y"),
        (rb"^ --More-- $", " "),
        (rb"^Confirm to overwrite current startup-config configuration", b"\ny\n"),
        (rb"^Confirm to overwrite the existed destination file?", b"\ny\n"),
        (rb"^Begin to receive file, please wait", b" "),
        (rb"#####", b" "),
    ]
    pattern_unprivileged_prompt = rb"^\S+>"
    pattern_syntax_error = (
        rb"% (Unrecognized command, and error|Invalid input) detected at "
        rb"'\^' marker.|% Ambiguous command:|interface error!|Incomplete "
        rb"command"
    )
    #    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_exit = "quit"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = rb"^\S+#"
    rogue_chars = [
        re.compile(rb"\s*\x1b\[74D\s+\x1b\[74D"),
        re.compile(rb"\s*\x1b\[74D\x1b\[K"),
        b"\r",
    ]
    rx_ifname = re.compile(r"(?P<number>[\d\/]+)$")
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("1/1")
        'e1/1'
        >>> Profile().convert_interface_name("e1/1")
        'e1/1'
        """
        match = self.rx_ifname.search(s)
        if match:
            return "e%s" % match.group("number")
        else:
            return s

    def get_interface_names(self, name):
        r = []
        if name.startswith("port "):
            r += [name[5:]]
        else:
            r += [name]
        return r

    def clean_lldp_neighbor(self, obj, neighbor):
        neighbor = super().clean_lldp_neighbor(obj, neighbor)
        if neighbor["remote_port_subtype"] == LLDP_PORT_SUBTYPE_COMPONENT:
            if neighbor.get("remote_port") is None:
                # self.script.logger.warning("Can't get remote_port_description")
                return neighbor
            # Platform reports single MAC address for every port
            # But leaks interface name to remote_port_description
            neighbor["remote_port_subtype"] = LLDP_PORT_SUBTYPE_NAME
            neighbor["remote_port"] = self.convert_interface_name(neighbor["remote_port"])
        return neighbor
