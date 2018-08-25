# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QSW2500
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QSW2500"
    pattern_more = [
        (r"^ --More-- $", " "),
        (r"^Confirm to overwrite current startup-config configuration "
            r"[Y/N]:", "\nY\n"),
        (r"^Confirm to overwrite current startup-config configuration",
            "\ny\n"),
        (r"^Confirm to overwrite the existed destination file?", "\ny\n"),
    ]
    pattern_unprivileged_prompt = r"^\S+>"
    pattern_syntax_error = r"% (?:Invalid input detected at '\^' marker|" \
                           r"(?:Ambiguous|Incomplete|.+Unknown) command)|" \
                           r"Error input in the position market by"
    command_disable_pager = "terminal page-break disable"
    telnet_send_on_connect = "\n"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_submit = "\r"
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[\.\-_\d\w]+)?" \
        r"(?:\(config[^\)]*\))?#"

    rx_ver = re.compile(
        r"^Product name: (?P<platform>\S+)\s*\n"
        r"^QOS\s+Version QOS_(?P<version>\S+)\.QSW.+\n"
        r"^Bootstrap\s+Version Bootstrap_(?P<bootprom>\S+)\.QSW.+\n"
        r"(^.*\n)?"
        r"^Hardware QSW\S+ Version Rev\.(?P<hardware>\S+)\s*\n"
        r"^\s*\n"
        r"^System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"^Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE
    )
