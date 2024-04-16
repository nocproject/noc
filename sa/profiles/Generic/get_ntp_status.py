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
from noc.sa.interfaces.base import IPv4Parameter, IPv6Parameter
from noc.core.snmp.render import render_bin
from noc.core.interface.error import InterfaceTypeError


class Script(BaseScript):
    name = "Generic.get_ntp_status"
    interface = IGetNTPStatus

    NTPv4_ASSOC_NAME_OID = mib["NTPv4-MIB::ntpAssocName"]
    NTPv4_ASSOC_ADDRESS_TYPE_OID = mib["NTPv4-MIB::ntpAssocAddressType"]
    NTPv4_ASSOC_ADDRESS_OID = mib["NTPv4-MIB::ntpAssocAddress"]
    NTPv4_ASSOC_STRATUM_OID = mib["NTPv4-MIB::ntpAssocStratum"]
    NTPv4_ASSOC_REF_ID_OID = mib["NTPv4-MIB::ntpAssocRefId"]

    NTPv4_STATUS_MODE_OID = mib["NTPv4-MIB::ntpEntStatusCurrentMode", 0]
    NTPv4_STATUS_STRATUM_OID = mib["NTPv4-MIB::ntpEntStatusStratum", 0]
    NTPv4_STATUS_NAME_OID = mib["NTPv4-MIB::ntpEntStatusActiveRefSourceName", 0]
    NTPv4_STATUS_ACTIVE_ID = mib["NTPv4-MIB::ntpEntStatusActiveRefSourceId", 0]

    def execute_snmp(self, **kwargs):
        ntp_associations = {}
        for (
            assoc_id,
            assoc_name,
            assoc_addr_type,
            assoc_address,
            assoc_stratum,
            assoc_refid,
        ) in self.snmp.get_tables(
            [
                self.NTPv4_ASSOC_NAME_OID,
                self.NTPv4_ASSOC_ADDRESS_TYPE_OID,
                self.NTPv4_ASSOC_ADDRESS_OID,
                self.NTPv4_ASSOC_STRATUM_OID,
                self.NTPv4_ASSOC_REF_ID_OID,
            ],
            display_hints={
                self.NTPv4_ASSOC_NAME_OID: render_bin,
                self.NTPv4_ASSOC_ADDRESS_OID: render_bin,
            },
        ):
            try:
                if len(assoc_name) == 4:
                    assoc_name = IPv4Parameter().clean(assoc_name)
                elif len(assoc_name) == 16:
                    assoc_name = IPv6Parameter().clean(assoc_name)
                else:
                    assoc_name = assoc_name.decode()
            except InterfaceTypeError as e:
                self.logger.debug("Cannot interpret name |%s| as IP (%s)", assoc_name, e)
                assoc_name = assoc_name.decode()

            # Remove zone index from address if exists
            # InetAddressType { ipv4(1), ipv6(2), ipv4z(3), ipv6z(4) }
            # InetAddress (SIZE (4|8|16|20))
            if assoc_addr_type == 3:
                assoc_address = assoc_address[:4]
            elif assoc_addr_type == 4:
                assoc_address = assoc_address[:16]

            ntp_associations[assoc_id] = {
                "name": assoc_name,
                "address": assoc_address,
                "stratum": assoc_stratum,
                "status": "unknown",
                "is_synchronized": False,
                "ref_id": assoc_refid,
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
            ntp_associations[current_id]["is_synchronized"] = True

        return [ntp_associations[x] for x in ntp_associations]
