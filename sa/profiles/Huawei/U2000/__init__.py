# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     U2000 media gateway
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.U2000"
    pattern_mml_continue = "^\s+Continuing"
    pattern_mml_end = "---\s+END"

    def get_mml_login(self, script):
        return self.get_mml_command("LGI", OP=script.credentials.get("user", ""),
                                    PWD=script.credentials.get("password", ""))

    rx_detect_code = re.compile("^RETCODE\s*=\s*(\d+)\s+(.+?)\s*$", re.MULTILINE)

    def parse_mml_header(self, header):
        match = self.rx_detect_code.search(header)
        if match:
            # If NE on M2000 not connect
            if str(match.group(2)) == "NE does not Connection" or str(match.group(2)) == "Register needed" or str(match.group(2)) == "Unknown exception":
                return None, match.group(2)
            elif int(match.group(1)) is not 0:
                return match.group(1), match.group(2)
        return None, "No result code"

    class mml_ne(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script, ip):
            self.script = script
            self.ip = ip

        def __enter__(self):
            """Enter switch context"""
            return self.script.mml("REG NE", IP="%s" % self.ip)

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                return self.script.mml("UNREG NE", IP="%s" % self.ip)
