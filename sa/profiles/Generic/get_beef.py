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
    CLI_ENCODING = "quopri"
    MIB_ENCODING = "base64"

    def execute(self, spec):
        result = {
            "version": self.BEEF_FORMAT,
            "uuid": str(uuid.uuid4()),
            "spec": spec["uuid"],
            "changed": datetime.datetime.now().isoformat(),
            "cli": [],
            "cli_fsm": [],
            "mib": [],
            "mib_encoding": self.MIB_ENCODING,
            "cli_encoding": self.CLI_ENCODING
        }
        # Process CLI answers
        result["cli"] = self.get_cli_results(spec)
        # Apply CLI fsm states
        result["cli_fsm"] = self.get_cli_fsm_results()
        # Apply MIB snapshot
        self.logger.debug("Collecting MIB snapshot")
        result["mib"] = self.get_snmp_results(spec)
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
            self.logger.debug("Collecting command: %s" % cmd)
            # Issue command
            try:
                self.cli(cmd)
            except self.ScriptError:
                pass
            # Append tracked data
            r += [{
                "names": cmd_answers[cmd],
                "request": cmd,
                "reply": [v.encode(self.CLI_ENCODING) for v in self.pop_cli_tracking()]
            }]
        self.stop_tracking()
        return r

    def get_cli_fsm_results(self):
        r = []
        for state, reply in self.iter_cli_fsm_tracking():
            r += [{
                "state": state,
                "reply": [v.encode(self.CLI_ENCODING) for v in reply]
            }]
        return r

    def collect_snmp(self, spec):
        # Collect
        for ans in spec["answers"]:
            if ans["type"] == "snmp-get":
                value = self.snmp.get(ans["value"], raw_varbinds=True)
                yield {
                    "oid": str(ans["value"]),
                    "value": value.encode(self.MIB_ENCODING).strip()
                }
            elif ans["type"] == "snmp-getnext":
                for oid, value in self.snmp.getnext(ans["value"], raw_varbinds=True):
                    yield {
                        "oid": str(oid),
                        "value": value.encode(self.MIB_ENCODING).strip()
                    }

    def get_snmp_results(self, spec):
        r = []
        # Deduplicate
        oids = {}
        for v in self.collect_snmp(spec):
            if v["oid"] in oids:
                continue  # Duplicate
            oids[v["oid"]] = tuple(int(x) for x in v["oid"].split("."))
            r += [v]
        # Sort
        return sorted(r, key=lambda x: oids[x["oid"]])
