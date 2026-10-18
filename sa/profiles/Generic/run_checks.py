# ---------------------------------------------------------------------
# Generic.run_checks
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.sa.interfaces.idiagnosticheck import IDiagnosticCheck
from noc.core.validators import is_ipv4


class Script(BaseScript):
    """
    Execute a script with check option
    """

    name = "Generic.run_checks"
    interface = IDiagnosticCheck

    def get_script_by_check(self, check) -> str | None:
        if check == IPing.check:
            return IPing.check_script
        return None

    def execute(self, checks: list[dict[str, Any]]):
        r = []
        for c in checks:
            if not is_ipv4(c["address"]):
                continue
            if c.get("script"):
                script = c["script"]
            else:
                script = self.get_script_by_check(c["name"])
            if not script or script not in self.scripts:
                r.append(
                    {
                        "check": c["name"],
                        "status": True,
                        "skipped": True,
                        "error": {
                            "code": "0",
                            "message": "Invalid script",
                        },
                    }
                )
                continue
            script = getattr(self.scripts, script)
            # interface: BaseInterface = script._interface
            if c["name"] != IPing.check:
                raise ValueError(f"Unsupported script check: {c['name']}")
            interface = IPing
            params = interface().get_check_params(c)
            result = script(**params)
            s = interface().clean_check_result(c, result)
            r.append(s)
        return r
