# ----------------------------------------------------------------------
# Axis.VAPIX.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.validators import is_int


class Script(BaseScript):
    name = "Axis.VAPIX.get_interfaces"
    interface = IGetInterfaces

    def execute(self):
        interfaces = []
        c = self.profile.get_dict(self)
        for i in range(4):  # for future models
            mac = c.get(f"root.Network.eth{i}.MACAddress")
            if mac is not None:
                iface = {
                    "name": f"eth{i}",
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": True,
                    "hints": ["noc::interface::role::uplink"],
                    "mac": mac,
                }
                sub = {
                    "name": f"eth{i}",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": mac,
                    "enabled_afi": [],
                }
                ip = c.get(f"root.Network.eth{i}.IPAddress")
                mask = c.get(f"root.Network.eth{i}.SubnetMask")
                if ip and ip != "0.0.0.0" and mask and mask != "0.0.0.0":
                    ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
                    sub["ipv4_addresses"] = [ip_address]
                    sub["enabled_afi"] += ["IPv4"]
                ipv6 = c.get("root.Network.eth%d.IPv6.IPAddresses" % i)
                if ipv6:
                    sub["ipv6_addresses"] = [ipv6]
                    sub["enabled_afi"] += ["IPv6"]
                iface["subinterfaces"] = [sub]
                interfaces += [iface]

        """
        root.Input.NbrOfInputs=1
        root.Input.I0.Name=Input 1
        root.Input.I0.Trig=closed
        """
        o = c.get("root.Input.NbrOfInputs")
        if is_int(o) and int(o) > 0:
            for i in range(int(o)):
                ifname = c.get(f"root.Input.I{i}.Name")
                iface = {
                    "name": ifname,
                    "type": "dry",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{"name": ifname, "admin_status": True, "oper_status": True}],
                }
                p = c.get(f"root.Input.I{i}.Trig")
                if p == "closed":
                    iface["enabled_protocols"] = ["DRY_NO"]
                else:
                    iface["enabled_protocols"] = ["DRY_NC"]
                interfaces += [iface]
        """
        root.Output.NbrOfOutputs=1
        root.Output.O0.Name=Output 1
        root.Output.O0.Active=closed
        root.Output.O0.Button=none
        root.Output.O0.PulseTime=0
        """
        o = c.get("root.Output.NbrOfOutputs")
        if is_int(o) and int(o) > 0:
            for i in range(int(o)):
                ifname = c.get(f"root.Output.O{i}.Name")
                iface = {
                    "name": ifname,
                    "type": "dry",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{"name": ifname, "admin_status": True, "oper_status": True}],
                }
                p = c.get(f"root.Output.O{i}.Active")
                if p == "closed":
                    iface["enabled_protocols"] = ["DRY_NO"]
                else:
                    iface["enabled_protocols"] = ["DRY_NC"]
                interfaces += [iface]

        return [{"interfaces": interfaces}]
