# ---------------------------------------------------------------------
# Generic.run_checks
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List, Dict, Any, Optional

# NOC modules
from noc.core.script.base import BaseScript
from noc.core.checkers.loader import loader
from noc.sa.interfaces.idiagnosticheck import IDiagnosticCheck
from noc.core.validators import is_ipv4


class Script(BaseScript):
    """
    Execute a script with check option
    """

    name = "Generic.run_checks"
    interface = IDiagnosticCheck

    def get_script_by_check(self, check) -> Optional[str]:
        iface = loader.get_interface_by_check(check)
        return iface.check_script

    def execute(self, checks: List[Dict[str, Any]]):
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
            interface = loader.get_interface_by_check(c["name"])
            if interface.check != c["name"]:
                raise ValueError("Interface %s Not supported check: %s" % (str(interface), c["name"]))
            params = interface().get_check_params(c)
            result = script(**params)
            s = interface().clean_check_result(c, result)
            r.append(s)
        return r
