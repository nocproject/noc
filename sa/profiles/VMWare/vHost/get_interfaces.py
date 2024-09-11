# ---------------------------------------------------------------------
# VMWare.vHost.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from ..vim import VIMScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(VIMScript):
    name = "VMWare.vHost.get_interfaces"
    interface = IGetInterfaces

    def execute_controller(self, hid: str):
        h = self.vim.get_host_by_id(hid)
        networks = {}
        fis = {"default": {"forwarding_instance": "default", "interfaces": []}}
        for n in h.network:
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
        uplinks = {}
        fis_nic = {}
        lags = {}
        interfaces = {}
        # h.config.network.vswitch
        for nic in h.config.network.pnic:
            iface = {
                "name": nic.device,
                "admin_status": bool(nic.linkSpeed),
                "oper_status": bool(nic.linkSpeed),
                "mac": nic.mac,
                "type": "physical",
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            interfaces[nic.device] = iface
        # h.config.network.proxySwitch
        for fi in h.config.network.proxySwitch:
            fis[fi.dvsUuid] = {"forwarding_instance": fi.dvsName, "interfaces": []}
            for u in fi.uplinkPort:
                uplinks[u.key] = {"name": u.value, "key": u.key, "fi": fi.dvsUuid}
            for nic in fi.pnic:
                fis_nic[nic.split("-")[-1]] = {"fi": fi.dvsUuid}
                # fis[fi.dvsUuid]["interfaces"] += [nic.split("-")[-1]]
            for lag in fi.hostLag:
                fis_nic[lag.lagName] = {"fi": fi.dvsUuid}
                lags[lag.lagKey] = lag.lagName
                interfaces[lag.lagName] = {
                    "name": lag.lagName,
                    "type": "aggregated",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [],
                }
                for u in lag.uplinkPort:
                    uplinks[u.key]["lag"] = lag.lagKey
                    interfaces[lag.lagName]["subinterfaces"] += [
                        {
                            "name": uplinks[u.key]["name"],
                            "admin_status": True,
                            "oper_status": True,
                            "enabled_afi": [],
                        }
                    ]
                for nic in fi.pnic:
                    interfaces[nic.split("-")[-1]]["aggregated_interface"] = lag.lagName
            if fi.hostLag:
                continue
            for s in fi.spec.backing.pnicSpec:
                fis_nic[s.pnicDevice]["uplink_key"] = s.uplinkPortKey
                fis_nic[s.pnicDevice]["uplink_portgroup_key"] = s.uplinkPortgroupKey
                interfaces[s.pnicDevice]["subinterfaces"] += [
                    {
                        "name": uplinks[s.uplinkPortKey]["name"],
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": [],
                    }
                ]
                if s.uplinkPortgroupKey not in networks:
                    continue
                interfaces[s.pnicDevice]["hints"] = [
                    f"noc::interface::port_group::{s.uplinkPortgroupKey}"
                ]
                if "tagged_vlans" in networks[s.uplinkPortgroupKey]:
                    interfaces[s.pnicDevice]["subinterfaces"][-1]["tagged_vlans"] = networks[
                        s.uplinkPortgroupKey
                    ]["tagged_vlans"]
                if "untagged_vlan" in networks[s.uplinkPortgroupKey]:
                    interfaces[s.pnicDevice]["subinterfaces"][-1]["untagged_vlan"] = networks[
                        s.uplinkPortgroupKey
                    ]["untagged_vlan"]
                interfaces[s.pnicDevice]["subinterfaces"][-1]["enabled_afi"] += ["BRIDGE"]
        for vnic in h.config.network.vnic:
            interfaces[vnic.device] = {
                "name": vnic.device,
                "admin_status": True,
                "oper_status": True,
                "mac": vnic.spec.mac,
                "type": "SVI",
                "enabled_afi": [],
                "subinterfaces": [],
            }
            if vnic.spec.distributedVirtualPort.switchUuid:
                fis_nic[vnic.device] = {"fi": vnic.spec.distributedVirtualPort.switchUuid}
            if vnic.spec.ip:
                ip = IPv4(vnic.spec.ip.ipAddress, vnic.spec.ip.subnetMask)
                interfaces[vnic.device]["subinterfaces"] += [
                    {
                        "name": vnic.device,
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [str(ip)],
                    }
                ]
        for vm in h.vm:
            for d in vm.config.hardware.device:
                if self.vim.has_internet_adapter(d) and d.backing.port:
                    name = f"vmnic-{d.backing.port.portKey}"
                    interfaces[name] = {
                        "name": name,
                        "admin_status": True,
                        "oper_status": True,
                        "mac": d.macAddress,
                        "type": "virtual",
                        "enabled_afi": [],
                        "subinterfaces": [],
                    }
                    if d.backing.port.portgroupKey in networks:
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
        for i, ii in interfaces.items():
            if i in fis_nic:
                f = fis_nic[i]["fi"]
            else:
                f = "default"
            fis[f]["interfaces"] += [ii]
        return list(fis.values())

    def execute(self, **kwargs):
        return self.execute_controller(hid=self.controller.local_id)
