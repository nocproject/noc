# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.WLC.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.WLC.get_cpe"
    interface = IGetCPE

    status_map = {
        1: "active",  # associated
        2: "inactive",  # disassociating
        3: "provisioning",  # downloading
    }

    def execute_snmp(self, **kwargs):
        r = []
        for (
            mac,
            ap_name,
            ap_location,
            ap_oper_status,
            ap_sw_ver,
            ap_model,
            ap_serial,
            ip_address,
            ap_type,
            ap_admin_status,
        ) in self.snmp.get_tables(
            [
                mib["AIRESPACE-WIRELESS-MIB::bsnAPName"],
                mib["AIRESPACE-WIRELESS-MIB::bsnAPLocation"],
                mib["AIRESPACE-WIRELESS-MIB::bsnAPOperationStatus"],
                mib["AIRESPACE-WIRELESS-MIB::bsnAPSoftwareVersion"],
                mib["AIRESPACE-WIRELESS-MIB::bsnAPModel"],
                mib["AIRESPACE-WIRELESS-MIB::bsnAPSerialNumber"],
                mib["AIRESPACE-WIRELESS-MIB::bsnApIpAddress"],
                mib["AIRESPACE-WIRELESS-MIB::bsnAPType"],
                mib["AIRESPACE-WIRELESS-MIB::bsnAPAdminStatus"],
            ]
        ):
            if ap_admin_status == "2":
                continue
            mac = ":".join(["%02X" % int(o) for o in mac.split(".")])
            r.append(
                {
                    "vendor": "Cisco",
                    "model": ap_model,
                    "version": ap_sw_ver,
                    "mac": mac,
                    "status": self.status_map[ap_oper_status],
                    "id": ap_name,  # Use int command show ap inventory NAME
                    "global_id": mac,
                    "type": "ap",
                    "name": ap_name,
                    "ip": ip_address,
                    "serial": ap_serial,
                    "description": "",
                    "location": ap_location,
                }
            )
        return r
