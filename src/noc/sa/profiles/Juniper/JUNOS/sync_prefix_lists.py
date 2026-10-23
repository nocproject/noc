# ---------------------------------------------------------------------
# Juniper.JUNOS.sync_prefix_lists
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.isyncprefixlists import ISyncPrefixLists

rx_pl = re.compile(
    r"^set policy-options policy-statement \S+ term pass from route-filter (\S+) (\S+)$"
)


class Script(BaseScript):
    name = "Juniper.JUNOS.sync_prefix_lists"
    interface = ISyncPrefixLists

    def execute(self, changed_prefix_lists):
        actions = []
        result = []
        for l in changed_prefix_lists:
            name = l["name"]
            if len(l["prefix_list"]) == 0:
                result.append({"name": name, "status": False})
                self.logger.error(f"Refusing to apply empty policy-option {name}")
                continue
            suffix = "exact" if l["strict"] else "orlonger"
            # Retrieve prefix list
            pl = self.cli(
                f"show configuration policy-options policy-statement {name} | display set"
            )
            applied_pl = set()
            for ln in pl.splitlines():
                match = rx_pl.match(ln)
                if match:
                    applied_pl.add(f"{match.group(1)} {match.group(2)}")
            # Build new prefix-list
            new_pl = {f"{x} {suffix}" for x in l["prefix_list"]}
            # Delete obsolete records
            actions += [
                f"delete policy-options policy-statement {name} term pass from route-filter {x}"
                for x in applied_pl.difference(new_pl)
            ]
            # Add new records
            actions += [
                f"set policy-options policy-statement {name} term pass from route-filter {x}"
                for x in new_pl.difference(applied_pl)
            ]
            result.append({"name": name, "status": True})
        # Apply changeset
        if actions:
            with self.configure():
                for cmd in actions:
                    self.cli(cmd)
        return result
