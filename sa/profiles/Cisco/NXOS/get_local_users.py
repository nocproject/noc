# ---------------------------------------------------------------------
# Cisco.NXOS.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Cisco.NXOS.get_local_users"
    interface = IGetLocalUsers

    def execute(self):
        data = self.cli("show user-account | no-more")
        r = []
        cu = {}
        for line in data.split("\n"):
            line = line.strip()
            if line.startswith("user:"):
                if cu:
                    r += [cu]
                cu = {"username": line[5:], "is_active": True}
            elif cu and line.startswith("roles:"):
                for role in line[6:].split(" "):
                    if role == "network-operator":
                        role = "operator"
                    elif role == "network-admin":
                        role = "superuser"
                    if "class" not in cu:
                        cu["class"] = role
                    elif cu["class"] == "superuser":
                        continue
                    else:
                        cu["class"] = role
        if cu:
            r += [cu]
        return r
