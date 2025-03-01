# ---------------------------------------------------------------------
# Generic.run_checks
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List, Dict, Any

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.idiagnosticheck import IDiagnosticCheck
from noc.core.validators import is_ipv4


class Script(BaseScript):
    """
    Execute a ping profile command
    """

    name = "Generic.run_checks"
    interface = IDiagnosticCheck

    def execute_ping(self, address):
        # Remote Ping
        r = self.scripts.ping(address=address)
        return {
            "check": "",
            "status": bool(r["success"]),
            "address": address,
            "metrics": [],
        }

    def execute_other(self, script, **kwargs):
        try:
            return getattr(self.scripts, script)(**kwargs)
        except AttributeError:
            return {
                "check": "",
                "status": True,
                "skipped": True,
                "error": {
                    "code": "0",
                    "message": "Invalid script",
                },
            }

    def execute(self, checks: List[Dict[str, Any]]):
        r = []
        for c in checks:
            if not is_ipv4(c["address"]):
                continue
            script = c["script"]
            if script not in self.scripts:
                r.append(
                    {
                        "check": "",
                        "status": True,
                        "skipped": True,
                        "error": {
                            "code": "0",
                            "message": "Invalid script",
                        },
                    }
                )
                continue
            if script == "ping":
                s = self.execute_ping(c["address"])
            else:
                s = self.execute_other(**c["data"])
            r.append(s)
        return r
