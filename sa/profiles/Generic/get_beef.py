# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid
import datetime
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetbeef import IGetBeef


class Script(BaseScript):
    """
    Enter a configuration mode and execute a list of CLI commands.
    return a list of results
    """
    name = "Generic.get_beef"
    interface = IGetBeef
    requires = []
    BEEF_FORMAT = "1"

    def execute(self, spec):
        result = {
            "version": self.BEEF_FORMAT,
            "uuid": str(uuid.uuid4()),
            "spec": spec["uuid"],
            "changed": datetime.datetime.now().isoformat(),
            "cli": [],
            "cli_fsm": [],
            "mib": []
        }
        # Process CLI answers
        self.start_tracking()
        for ans in spec["answers"]:
            if ans["type"] == "cli":
                result["cli"] += [self.get_cli_result(ans)]
        self.stop_tracking()
        # Apply CLI fsm states
        self.logger.debug("Collecting CLI beef")
        for state, reply in self.iter_cli_fsm_tracking():
            result["cli_fsm"] += [{
                "state": state,
                "reply": reply
            }]
        # Apply MIB snapshot
        self.logger.debug("Collecting MIB snapshot")
        result["mib"] = self.get_mib_snapshot()
        # Process version reply
        result["box"] = self.scripts.get_version()
        return result

    def get_cli_result(self, ans):
        """
        Process CLI answer
        ans.value contains CLI command
        :param ans:
        :param stream:
        :return:
        """
        # Issue command
        self.cli(ans["value"])
        # Return tracked data
        return {
            "name": ans["name"],
            "request": ans["value"],
            "reply": self.pop_cli_tracking()
        }

    def get_mib_snapshot(self):
        r = []
        for oid, value in self.snmp.getnext("1.3.6", raw_varbinds=True):
            r += [{
                "oid": str(oid),
                "value": value.encode("hex")
            }]
        return r
