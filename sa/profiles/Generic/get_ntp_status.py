# ---------------------------------------------------------------------
# Generic.get_ntp_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetntpstatus import IGetNTPStatus
from noc.core.mib import mib
from noc.sa.interfaces.base import IPv4Parameter
from noc.core.snmp.render import render_bin


class Script(BaseScript):
    name = "Generic.get_ntp_status"
    interface = IGetNTPStatus

    NTPv4_REF_ID_OID = mib["NTPv4-MIB::ntpAssocRefId"]
    NTPv4_STRATUM_OID = mib["NTPv4-MIB::ntpAssocStratum"]
    NTPv4_ADDRESS_OID = mib["NTPv4-MIB::ntpAssocAddress"]
    NTPv4_NAME_OID = mib["NTPv4-MIB::ntpAssocName"]

    NTPv4_STATUS_MODE_OID = mib["NTPv4-MIB::ntpEntStatusCurrentMode", 0]
    NTPv4_STATUS_STRATUM_OID = mib["NTPv4-MIB::ntpEntStatusStratum", 0]
    NTPv4_STATUS_NAME_OID = mib["NTPv4-MIB::ntpEntStatusActiveRefSourceName", 0]
    NTPv4_STATUS_ACTIVE_ID = mib["NTPv4-MIB::ntpEntStatusActiveRefSourceId", 0]

    def execute_snmp(self, **kwargs):
        ntp_associations = {}
        for x in self.snmp.get_tables(
            [
                self.NTPv4_NAME_OID,
                self.NTPv4_ADDRESS_OID,
                self.NTPv4_STRATUM_OID,
                self.NTPv4_REF_ID_OID,
            ],
            display_hints={
                self.NTPv4_NAME_OID: render_bin,
                self.NTPv4_ADDRESS_OID: render_bin,
            },
        ):
            assoc_name = ""
            if len(x[1]) == 4:
                assoc_name = IPv4Parameter().clean(x[1])
            else:
                assoc_name = x[1].decode()

            ntp_associations[x[0]] = {
                "name": assoc_name,
                "address": x[2],
                "stratum": x[3],
                "status": "unknown",
                "is_synchronized": False,
                "ref_id": x[4],
            }

        status = self.snmp.get(
            {
                "mode": self.NTPv4_STATUS_MODE_OID,
                "stratum": self.NTPv4_STATUS_STRATUM_OID,
                "name": self.NTPv4_STATUS_NAME_OID,
                "active_id": self.NTPv4_STATUS_ACTIVE_ID,
            }
        )

        if status["active_id"] in ntp_associations:
            current_id = status["active_id"]
            ntp_associations[current_id]["status"] = "master"

        return [ntp_associations[x] for x in ntp_associations]
