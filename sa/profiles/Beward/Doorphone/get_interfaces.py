# ---------------------------------------------------------------------
# Beward.Doorphone.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Beward.Doorphone.get_interfaces"
    cache = True
    interface = IGetInterfaces

    iftype_map = {6: "physical", 24: "loopback"}

    status_map = {1: True, 2: False}

    def get_correct_result(self, mib: str, mapper: dict = None) -> dict:
        """
        Returns dict in the form {ifindex: value}

        :params:
            mib - oid to get the value
            mapper - mapper for ifType data
        :return: dict with data
        """

        result = {}
        for oid, value in self.snmp.getnext(mib):
            ifindex = oid.split(".")[-1]
            if mapper is None:
                result[ifindex] = value
            else:
                result[ifindex] = mapper.get(value)
        return result

    def get_correct_mac(self, mib: str) -> dict:
        """
        Returns dict in the form {ifindex: mac}

        :params:
            mib - oid to get the mac
        :return: dict with data
        """

        result = {}
        for oid, mac in self.snmp.getnext(mib, display_hints={mib: render_mac}):
            index = oid.split(".")[-1]
            result[index] = mac
        return result

    def execute_snmp(self):
        names = self.get_correct_result(mib["IF-MIB::ifDescr"])
        types = self.get_correct_result(mib["IF-MIB::ifType"], mapper=self.iftype_map)
        mac_address = self.get_correct_mac(mib["IF-MIB::ifPhysAddress"])
        oper_status = self.get_correct_result(mib["IF-MIB::ifOperStatus"], mapper=self.status_map)
        admin_status = self.get_correct_result(mib["IF-MIB::ifAdminStatus"], mapper=self.status_map)

        interfaces = []
        for index, value in names.items():
            interface = {
                "type": types[index],
                "name": value,
                "admin_status": admin_status[index],
                "oper_status": oper_status[index],
                "snmp_ifindex": index,
                "subinterfaces": [],
            }
            if mac_address[index]:
                interface["mac"] = mac_address[index]
            interfaces.append(interface)

        return [{"interfaces": interfaces}]
