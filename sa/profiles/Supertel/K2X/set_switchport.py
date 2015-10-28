# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.set_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import ISetSwitchport
from noc.lib.text import list_to_ranges


class Script(BaseScript):
    name = "Supertel.K2X.set_switchport"
    interface = ISetSwitchport

    def execute(self, configs, protect_switchport=True, protect_type=True,
                debug=False):
        def is_access(c):
            return "untagged" in c and ("tagged" not in c or not c["tagged"])

        # Get existing switchports. interface -> config
        ports = dict((p["interface"], p)
                     for p in self.scripts.get_switchport())

        # Validate restrictions
        errors = []
        for c in configs:
            iface = c["interface"]
            if protect_switchport and iface not in ports:
                errors += ["Interface '%s' is not switchport" % iface]
            if (protect_type and
                    is_access(c) != is_access(ports[iface])):
                errors += ["Invalid port type for interface '%s'" % iface]
        if errors:
            return {
                "status": False,
                "message": ".\n".join(errors)
            }

        # Prepare scenario
        commands = []
        for c in configs:
            ic = []
            iface = c["interface"]
            p = ports[iface]
            # Check description
            if ("description" in c and c["description"] and
                ("description" not in p or
                 c["description"] != p["description"])):
                ic += [" description %s" % c["description"]]
            # Check status
            if c["status"] and not p["status"]:
                ic += [" no shutdown"]
            elif p["status"] and not c["status"]:
                ic += [" shutdown"]
            # Check switchport
            if iface not in ports:
                ic += [" switchport"]
            if is_access(c):
                # Configuring access port
                if not is_access(p):
                    # trunk -> access
                    ic += [" no switchport trunk native vlan"]
                    ic += [" switchport mode access"]
                # @todo: set vlan only when necessary
                ic += [" switchport access vlan %d" % c["untagged"]]
            else:
                # Configuring trunk port
                if is_access(p):
                    # access -> trunk
                    ic += [" no switchport access vlan"]
                    ic += [" switchport mode trunk"]
                if ("untagged" in c and (
                        "untagged" not in p or
                        c["untagged"] != p["untagged"]) or
                        is_access(p)):
                    # Add native vlan
                    ic += [" switchport trunk native vlan %d" % c["untagged"]]
                if "untagged" not in c and "untagged" in p:
                    # Remove native vlan
                    ic += [" no switchport trunk native vlan"]
                cv = list_to_ranges(c["tagged"])
                pv = list_to_ranges(p["tagged"])
                if cv != pv:
                    # Change untagged vlans
                    ic += [" switchport trunk allowed vlan add %s" % cv]
            # Configure edge-port
            ept = {
                True: "spanning-tree portfast",
                False: "spanning-tree portfast auto"
            }
            if is_access(c) != is_access(p):
                # access <-> trunk. Remove old edgeport settings
                ic += [" no %s" % ept[not is_access(c)]]
            if c["edge_port"]:
                ic += [" %s" % ept[is_access(c)]]
            else:
                ic += [" no %s" % ept[is_access(c)]]
            #
            if ic:
                if iface[:2] == 'ch':
                    commands += ["interface port-channel %s" % iface[2:]
                                 ] + ic + [" exit"]
                else:
                    commands += ["interface ethernet %s" % iface
                                 ] + ic + [" exit"]
        # Apply commands
        if not debug and commands:
            with self.configure():
                for c in commands:
                    self.cli(c)
            self.save_config()
        # Return result
        return {
            "status": True,
            "message": "Ok",
            "log": "\n".join(commands)
        }
