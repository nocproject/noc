# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QSW2500
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.validators import is_int


class Profile(BaseProfile):
    name = "Qtech.QSW2500"

    pattern_more = [
        (rb"^ --More-- $", b" "),
        (rb"^Confirm to overwrite current startup-config configuration [Y/N]:", b"\nY\n"),
        (rb"^Confirm to overwrite current startup-config configuration", b"\ny\n"),
        (rb"^Confirm to overwrite the existed destination file?", b"\ny\n"),
    ]
    pattern_unprivileged_prompt = rb"^\S+>"
    pattern_syntax_error = (
        rb"% (?:Invalid input detected at '\^' marker|"
        rb"(?:Ambiguous|Incomplete|.+Unknown) command)|"
        rb"Error input in the position market by"
    )
    command_disable_pager = "terminal page-break disable"
    telnet_send_on_connect = b"\n"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_submit = b"\r"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[\.\-_\d\w]+)?(?:\(config[^\)]*\))?#"

    rx_ver = re.compile(
        r"^\s*Product name: (?P<platform>\S+)\s*\n"
        r"^\s*QOS\s+[Vv]ersion QOS_(?P<version>\S+)\.QSW.+\n"
        r"^\s*(Bootstrap\s+Version )?Bootstrap_(?P<bootprom>\S+)\.QSW.+\n"
        r"(^.*\n)?"
        r"^\s*Hardware QSW\S+ (Version )?Rev\.(?P<hardware>\S+)\s*\n"
        r"^\s*\n"
        r"^\s*(System )?[Mm][Aa][Cc]\s*[Aa]ddress( is)?\s*:\s*(?P<mac>\S+)\s*\n"
        r"^\s*Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    def convert_interface_name(self, interface):
        if is_int(interface):
            return "port%s" % interface
        if " " in interface:
            return interface.replace(" ", "")
        return interface
