# ---------------------------------------------------------------------
# VMWare.vMachine.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "VMWare.vMachine.get_interfaces"
    interface = IGetInterfaces

    def execute_controller(self, hid: str):
        vm = self.vim.get_vm_by_id(hid)
        interfaces = {}
        networks = {}
        for n in vm.network:
            if n._moId.startswith("network"):
                # Local Network
                continue
            if n.config.key not in networks:
                networks[n.config.key] = {"name": n.name}
            vlan = n.config.defaultPortConfig.vlan
            if not vlan.vlanId:
                continue
            networks[n.config.key]["ports"] = list(n.portKeys)
            if isinstance(vlan.vlanId, list):
                # Tunked ports
                networks[n.config.key]["tagged_vlans"] = list(
                    range(vlan.vlanId[0].start or 1, vlan.vlanId[0].end + 1)
                )
            else:
                networks[n.config.key]["untagged_vlan"] = vlan.vlanId
        for d in vm.config.hardware.device:
            if self.vim.has_internet_adapter(d):
                name = f"vmnic-{d.key}"
                interfaces[name] = {
                    "name": name,
                    "admin_status": True,
                    "oper_status": True,
                    "mac": d.macAddress,
                    "type": "SVI",
                    "enabled_afi": [],
                    "subinterfaces": [],
                }
                if d.backing.port and d.backing.port.portgroupKey in networks:
                    interfaces[name]["hints"] = [
                        f"noc::interface::port_group::{d.backing.port.portgroupKey}"
                    ]
                    interfaces[name]["subinterfaces"] += [
                        {
                            "name": name,
                            "admin_status": True,
                            "oper_status": True,
                            "enabled_afi": ["BRIDGE"],
                            "untagged_vlan": networks[d.backing.port.portgroupKey].get(
                                "untagged_vlan"
                            ),
                            "tagged_vlans": networks[d.backing.port.portgroupKey].get(
                                "tagged_vlans"
                            ),
                        }
                    ]
        return [{"forwarding_instance": "default", "interfaces": list(interfaces.values())}]

    def execute(self, **kwargs):
        return self.execute_controller(hid=self.controller.local_id)
