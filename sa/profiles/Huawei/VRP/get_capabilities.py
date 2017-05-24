# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Huawei.VRP.get_capabilities"

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        try:
            r = self.cli("display stp global | include Enabled")
            return "Enabled" in r
        except self.CLISyntaxError:
            try:
                r = self.cli("display stp | include disabled")
                return "Protocol Status" not in r
            except self.CLISyntaxError:
                r = self.cli("display stp")
                return "Protocol Status" not in r

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has LLDP enabled
        """
        r = self.cli("display lldp local")
        return "LLDP is not enabled" not in r \
            and "Global status of LLDP: Disable" not in r \
                and "LLDP enable status:           disable" not in r

    @false_on_cli_error
    def has_ndp(self):
        """
        Check box has NDP enabled
        """
        r = self.cli("display ndp")
        return "enabled" in r

    @false_on_cli_error
    def has_bfd(self):
        """
        Check box has BFD enabled
        """
        r = self.cli("display bfd configuration all")
        return not "Please enable BFD in global mode first" in r

    @false_on_cli_error
    def has_udld(self):
        """
        Check box has UDLD enabled
        """
        r = self.cli("display dldp")
        return "Global DLDP is not enabled" not in r \
            and "DLDP global status : disable" not in r

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        out = self.cli("display stack")
        if "device is not in stacking" in out:
            return []
        r = self.profile.parse_table(out, part_name="stack")
        return [l[0] for l in r["stack"]["table"]] if "table" in r["stack"] else []

    @false_on_cli_error
    def has_lacp(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("display lacp statistics eth-trunk")
        return r

    def execute_platform(self, caps):
        if self.has_ndp():
            caps["Huawei | NDP"] = True
        if self.has_lacp():
            caps["Network | LACP"] = True
        s = self.has_stack()
        if s:
            caps["Stack | Members"] = len(s) if len(s) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
