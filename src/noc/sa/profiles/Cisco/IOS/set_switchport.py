# ---------------------------------------------------------------------
# Cisco.IOS.set_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.isetswitchport import ISetSwitchport
from noc.core.text import list_to_ranges


class Script(BaseScript):
    name = "Cisco.IOS.set_switchport"
    interface = ISetSwitchport

    def execute(self, configs, protect_switchport=True, protect_type=True, debug=False):
        def is_access(c):
            return "untagged" in c and ("tagged" not in c or not c["tagged"])

        # Get existing switchports. interface -> config
        ports = {p["interface"]: p for p in self.scripts.get_switchport()}
        # Validate restrictions
        errors = []
        for c in configs:
            iface = c["interface"]
            if protect_switchport and iface not in ports:
                errors.append(f"Interface '{iface}' is not switchport")
            if protect_type and is_access(c) != is_access(ports[iface]):
                errors.append(f"Invalid port type for interface '{iface}'")
        if errors:
            return {"status": False, "message": ".\n".join(errors)}
        # Check wrether edge ports can be configured
        skip_edge_port = self.is_me_series
        # Prepare scenario
        commands = []
        for c in configs:
            ic = []
            iface = c["interface"]
            p = ports[iface]
            # Check description
            if (
                "description" in c
                and c["description"]
                and ("description" not in p or c["description"] != p["description"])
            ):
                ic.append(f" description {c['description']}")
            # Check status
            if c["status"] and not p["status"]:
                ic.append(" no shutdown")
            elif p["status"] and not c["status"]:
                ic.append(" shutdown")
            # Check switchport
            if iface not in ports:
                ic.append(" switchport")
            if is_access(c):
                # Configuring access port
                if not is_access(p):
                    # trunk -> access
                    ic.append(" switchport mode access")
                    ic.append(" no switchport trunk allowed vlan")
                    ic.append(" no switchport trunk native vlan")
                # @todo: set vlan only when necessary
                ic.append(f" switchport access vlan {int(c['untagged'])}")
            else:
                # Configuring trunk port
                if is_access(p):
                    # access -> trunk
                    # ic += [" switchport trunk encapsulation dot1q"]
                    ic.append(" switchport mode trunk")
                    ic.append(" no switchport access vlan")
                if (
                    "untagged" in c and ("untagged" not in p or c["untagged"] != p["untagged"])
                ) or is_access(p):
                    # Add native vlan
                    ic.append(f" switchport trunk native vlan {int(c['untagged'])}")
                if "untagged" not in c and "untagged" in p:
                    # Remove native vlan
                    ic.append(" no switchport trunk native vlan")
                cv = list_to_ranges(c["tagged"])
                pv = list_to_ranges(p["tagged"])
                if cv != pv:
                    # Change untagged vlans
                    ic.append(f" switchport trunk allowed vlan {cv}")
            # Configure edge-port
            if not skip_edge_port:
                ept = {True: "spanning-tree portfast", False: "spanning-tree portfast trunk"}
                if is_access(c) != is_access(p):
                    # access <-> trunk. Remove old edgeport settings
                    ic.append(f" no {ept[not is_access(c)]}")
                if c["edge_port"]:
                    ic.append(f" {ept[is_access(c)]}")
                else:
                    ic.append(f" no {ept[is_access(c)]}")
            if ic:
                commands += [f"interface {iface}", *ic, " exit"]
        # Apply commands
        if not debug and commands:
            with self.configure():
                for c in commands:
                    self.cli(c)
            self.save_config()
        # Return result
        return {"status": True, "message": "Ok", "log": "\n".join(commands)}
