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
from collections import defaultdict
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
            "mib": [],
            "mib_encoding": "base64"
        }
        # Process CLI answers
        result["cli"] = self.get_cli_results(spec)
        # Apply CLI fsm states
        result["cli_fsm"] = self.get_cli_fsm_results()
        # Apply MIB snapshot
        self.logger.debug("Collecting MIB snapshot")
        result["mib"] = self.get_mib_snapshot()
        # Process version reply
        result["box"] = self.scripts.get_version()
        return result

    def get_cli_results(self, spec):
        """
        Returns "cli" section
        :param spec:
        :return:
        """
        r = []
        # Group by commands
        cmd_answers = defaultdict(list)
        for ans in spec["answers"]:
            if ans["type"] == "cli":
                cmd_answers[ans["value"]] += [ans["name"]]
        if not cmd_answers:
            return []
        self.logger.debug("Collecting CLI beef")
        self.start_tracking()
        for cmd in cmd_answers:
            # Issue command
            try:
                self.cli(cmd)
            except self.ScriptError:
                pass
            # Append tracked data
            r += [{
                "names": cmd_answers[cmd],
                "request": cmd,
                "reply": self.pop_cli_tracking()
            }]
        self.stop_tracking()
        return r

    def get_cli_fsm_results(self):
        r = []
        for state, reply in self.iter_cli_fsm_tracking():
            r += [{
                "state": state,
                "reply": reply
            }]
        return r

    def get_mib_snapshot(self):
        r = []
        for oid, value in self.snmp.getnext("1.3.6", raw_varbinds=True):
            r += [{
                "oid": str(oid),
                "value": value.encode("base64").strip()
            }]
        return r
