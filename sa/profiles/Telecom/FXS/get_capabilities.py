# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Telecom.FXS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Telecom.FXS.get_capabilities"
    cache = True

    def execute_platform_snmp(self, caps):
        wan_ip = self.snmp.get("1.3.6.1.4.1.40248.4.1.6")
        mask = self.snmp.get("1.3.6.1.4.1.40248.4.1.7")
        gateway = self.snmp.get("1.3.6.1.4.1.40248.4.1.8")
        protocol_name = self.snmp.get("1.3.6.1.4.1.40248.4.1.1")
        server_status = self.snmp.get("1.3.6.1.4.1.40248.4.1.127")

        caps["TelecomFXS | DeviceWANIP"] = "" if wan_ip is None else wan_ip
        caps["TelecomFXS | DeviceMask"] = "" if mask is None else mask
        caps["TelecomFXS | DeviceGateway"] = "" if gateway is None else gateway
        caps["TelecomFXS | ProtocolName"] = "" if protocol_name is None else protocol_name
        caps["TelecomFXS | SIPServerStatus"] = "" if server_status is None else str(server_status)
