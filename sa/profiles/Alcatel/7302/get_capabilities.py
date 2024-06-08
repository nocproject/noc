# ----------------------------------------------------------------------
# Alcatel.7302.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.text import parse_table
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error


class Script(BaseScript):
    name = "Alcatel.7302.get_capabilities"

    # checking caps "SNMP | MIB | ASAM-MIB" to collect "Interface | xDSL | Line..." metrics
    # OID 1.3.6.1.4.1.637.61.1.39 is needed to collect xDSL metrics on the device
    CHECK_SNMP_GETNEXT = {"SNMP | MIB | ASAM-MIB": "1.3.6.1.4.1.637.61.1.39"}

    @false_on_cli_error
    def has_stp_cli(self):
        try:
            # MSTP Check
            mstp = self.cli("show mstp port-instance")
            if "instance count : 0" in mstp or "port-instance count : 0" in mstp:
                return False
            return True
        except self.CLISyntaxError:
            pass
        # RSTP Check
        rstp = self.cli("show rstp port-info")
        r = "port-info count : 0" not in rstp
        return r

    @false_on_cli_error
    def has_slots_cli(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show equipment slot")
        return [
            p[0].split("/")[-1]
            for p in parse_table(r)
            if p[0].startswith("lt") and p[4] == "available"
        ]

    @false_on_snmp_error
    def has_slots_snmp(self):
        r = []
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.637.61.1.23.3.1.8", bulk=False):
            if v != 1:
                # availability != available
                continue
            self.logger.info("OID: %s, status: %d", oid, v)
            slot_id = oid.rsplit(".", 1)[-1]
            rack, shelf, slot = self.profile.get_slot(int(slot_id))
            if not 3 < slot < 18:
                # NCU & ACU
                continue
            r += [str(slot)]
        return r

    def execute_platform_cli(self, caps):
        s = self.has_slots_cli()
        if s:
            caps["Slot | Members"] = len(s) if len(s) != 1 else 0
            caps["Slot | Member Ids"] = " | ".join(s)

    def execute_platform_snmp(self, caps):
        s = self.has_slots_snmp()
        if s:
            caps["Slot | Members"] = len(s) if len(s) != 1 else 0
            caps["Slot | Member Ids"] = " | ".join(s)
