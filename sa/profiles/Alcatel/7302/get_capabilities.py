# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.7302.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.text import parse_table
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Alcatel.7302.get_capabilities"

    @false_on_cli_error
    def has_stp(self):
        try:
            # MSTP Check
            mstp = self.cli("show mstp port-instance")
            if "instance count : 0" in mstp or "port-instance count : 0" in mstp:
                print("False")
                return False
            print("True")
            return True
        except self.CLISyntaxError:
            pass
        # RSTP Check
        rstp = self.cli("show rstp port-info")
        r = "port-info count : 0" not in rstp
        return r

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show equipment slot")
        return [p[0].split("/")[-1] for p in parse_table(r) if p[0].startswith("lt") and p[3] == "no-error"]

    def execute_platform(self, caps):
        s = self.has_stack()
        if s:
            caps["Stack | Members"] = len(s) if len(s) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
