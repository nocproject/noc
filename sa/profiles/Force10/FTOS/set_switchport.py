# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.set_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
from collections import defaultdict
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import ISetSwitchport


class Script(NOCScript):
    name = "Force10.FTOS.set_switchport"
    implements = [ISetSwitchport]

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
        add_untagged = defaultdict(list)  # vlan -> interfaces
        remove_untagged = defaultdict(list)  # vlan -> interfaces
        add_tagged = defaultdict(list)  # vlan -> interfaces
        remove_tagged = defaultdict(list)  # vlan -> interfaces
        # Configure interfaces
        for c in configs:
            ic = []
            iface = c["interface"]
            if iface not in ports:
                # Not switchport
                ic += [" switchport"]
                ports[iface] = {"status": False, "tagged": []}
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
            # @todo: edgeport
            # Check switchport
            if iface not in ports:
                ic += [" switchport"]
            # Save commands
            if ic:
                commands += ["interface %s" % iface] + ic + [" exit"]
            # Prepare VLAN mappings
            if is_access(c):
                # Configuring access port
                if not is_access(p):
                    # trunk -> access
                    for v in p["tagged"]:
                        remove_tagged[v] += [iface]
                if "untagged" in p and c["untagged"] != p["untagged"]:
                    remove_untagged[p["untagged"]] += [iface]
                add_untagged[c["untagged"]] += [iface]
            else:
                # Configuring trunk port
                if ("untagged" in p and
                    ("untagged" not in c or p["untagged"] != c["untagged"])):
                    remove_untagged[p["untagged"]] += [iface]
                if "untagged" in c:
                    add_untagged[c["untagged"]] += [iface]
                cv = set(c["tagged"])
                pv = set(p["tagged"])
                for v in cv - pv:
                    add_tagged[v] += [iface]
                for v in pv - cv:
                    remove_tagged[v] += [iface]
        # Do not remove interfaces from vlan 1
        if 1 in remove_untagged:
            del remove_untagged[1]
        if 1 in remove_tagged:
            del remove_tagged[1]
        # Process VLAN mappings
        vlans = sorted(set(
            add_untagged.keys() + add_tagged.keys() +
            remove_untagged.keys() + remove_tagged.keys()
        ))
        print "@@@@@ U REMOVE", remove_untagged, "ADD", add_untagged
        print "@@@@@ T REMOVE", remove_tagged, "ADD", add_tagged
        # Remove interfaces
        for v in vlans:
            vc = []
            for i in remove_untagged[v]:
                if i not in add_untagged[v]:
                    vc += [" no untagged %s" % i]
            for i in remove_tagged[v]:
                if i not in add_tagged[v]:
                    vc += [" no tagged %s" % i]
            if vc:
                commands += ["interface Vlan %d" % v] + vc + [" exit"]
        # Add interfaces
        for v in vlans:
            vc = []
            for i in add_untagged[v]:
                if i not in remove_untagged[v]:
                    vc += [" untagged %s" % i]
            for i in add_tagged[v]:
                if i not in remove_tagged[v]:
                    vc += [" tagged %s" % i]
            if vc:
                commands += ["interface Vlan %d" % v] + vc + [" exit"]
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
