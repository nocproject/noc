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
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        try:
            res = self.cli("display stp global | include Protocol")
            return "Enabled" in r
        except self.CLISyntaxError:
            try:
                res = self.cli("display stp | include disabled")
                return "Protocol Status" not in r
            except self.CLISyntaxError:
                res = self.cli("display stp")
                return "Protocol Status" not in r

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        res = self.cli("display lldp local")
        return "LLDP is not enabled" not in r \
            and "Global status of LLDP: Disable" not in r \
                and "LLDP enable status:           disable" not in res

    @false_on_cli_error
    def has_ndp_cli(self):
        """
        Check box has NDP enabled
        """
        res = self.cli("display ndp")
        return "enabled" in res

    @false_on_cli_error
    def has_bfd_cli(self):
        """
        Check box has BFD enabled
        """
        res = self.cli("display bfd configuration all")
        return res and not ("Please enable BFD in global mode first" in r)

    @false_on_cli_error
    def has_udld_cli(self):
        """
        Check box has UDLD enabled
        """
        res = self.cli("display dldp")
        return "Global DLDP is not enabled" not in res \
            and "DLDP global status : disable" not in res

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        out = self.cli("display stack")
        if "device is not in stacking" in out:
            return []
        res = self.profile.parse_table(out, part_name="stack")
        return [l[0] for l in res["stack"]["table"]] if "table" in res["stack"] else []

    def has_slot(self):
        """
        For devices contains more one slots get count
        :return:
        """
        slots = set([])
        if "ME60" in self.version.get("platform", ""):
            # ME60-X16A, ME60-X8A, ME60-X16, ME60-X8, ME60-X3 filter LPU
            n = self.version.get("platform", "").strip("A")
            n = int(n[6:])

            if self.has_snmp():
                oids = ["1.3.6.1.2.1.47.1.1.1.1.5", "1.3.6.1.2.1.47.1.1.1.1.6"]
                s_pos = 0
                for index, type, pos in list(self.snmp.get_tables(oids, bulk=True)):
                    print index, type, pos
                    if type == 5:
                        s_pos = pos
                    elif type == 9:
                        slots.add(s_pos)

            return [str(x) for x in slots if x <= n]

        return slots

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check stack members
        :return:
        """
        res = self.cli("display lacp statistics eth-trunk")
        return res

    def execute_platform_cli(self, caps):
        if self.has_ndp_cli():
            caps["Huawei | NDP"] = True
        stk = self.has_stack()
        slt = self.has_slot()
        if stk:
            caps["Stack | Members"] = len(stk) if len(stk) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(stk)
        if sl:
            caps["Slot | Members"] = len(slt) if len(slt) != 1 else 0
            caps["Slot | Member Ids"] = " | ".join(slt)

    def execute_platform_snmp(self, caps):
        slt = self.has_slot()
        if slt:
            caps["Slot | Members"] = len(slt) if len(slt) != 1 else 0
            caps["Slot | Member Ids"] = " | ".join(slt)
