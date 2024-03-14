# ----------------------------------------------------------------------
# Telecom.CPE.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Telecom.CPE.get_interfaces"
    interface = IGetInterfaces

    type_map = {
        6: "physical",
        24: "loopback",
    }

    status_map = {
        1: True,
        2: False,
        3: True,
    }

    def get_res_by_oid(self, oid: str, mapper: dict = None) -> dict:
        "Возвращает {ifindex:name}"

        if mapper is None:
            mapper = {}

        result = {}
        for oid_, v in self.snmp.getnext(oid, bulk=False):
            index = oid_.split(oid)[-1][1:]
            result[index] = v
            if mapper:
                result[index] = mapper.get(v)
        return result

    def get_mac_by_oid(self, oid: str) -> dict:
        "Возвращает {ifindex:mac}"
        result = {}
        # mac = self.snmp.get
        for oid_, v in self.snmp.getnext(oid, display_hints={oid: render_mac}):
            index = oid_.split(oid)[-1][1:]
            result[index] = v
        return result

    def execute_snmp(self):
        name = self.get_res_by_oid(mib["IF-MIB::ifDescr"])
        ifType = self.get_res_by_oid(mib["IF-MIB::ifType"], self.type_map)
        # ifSpeed = self.get_res_by_oid(mib["IF-MIB::ifSpeed"])
        ifPhysAddress = self.get_mac_by_oid(mib["IF-MIB::ifPhysAddress"])
        ifAdminStatus = self.get_res_by_oid(mib["IF-MIB::ifAdminStatus"], self.status_map)
        ifOperStatus = self.get_res_by_oid(mib["IF-MIB::ifOperStatus"], self.status_map)

        interfaces = []
        for i, n in name.items():
            interface = {
                "type": ifType[i],
                "name": n,
                "admin_status": ifAdminStatus[i],
                "oper_status": ifOperStatus[i],
                "snmp_ifindex": i,
                "subinterfaces": [],
            }
            if ifPhysAddress[i]:
                interface["mac"] = ifPhysAddress[i]
            if n.startswith("wlan"):
                interface["hints"] = ["technology::radio::wifi"]
            self.logger.info(f"interface = {interface}")
            interfaces.append(interface)

        return [{"interfaces": interfaces}]
