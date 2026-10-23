# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig

SEP = "=" * 40


class Script(BaseScript):
    name = "Cisco.ASA.get_config"
    interface = IGetConfig

    def get_config(self, path):
        config = self.cli("more " + path)
        config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)

    def execute_cli(self, **kwargs):
        context_mode = self.capabilities.get("Cisco | ASA | Security | Context | Mode", "")
        if context_mode != "multiple":
            config = self.cli("more system:running-config")
            config = self.strip_first_lines(config, 3)
            return self.cleaned_config(config)

        self.cli("changeto system")
        v = self.cli("show context")
        contexts = []
        nextinterface = False
        r = v.splitlines()
        headline = r.pop(0).split()
        headline[0] = headline[0] + headline.pop(1)
        for line in r:
            """Get context list from table"""
            line = line.strip()
            if line == "":
                continue
            row = line.split()
            if row[0] == "Total":
                """Skip last row (number of context)"""
                break
            if nextinterface:
                """If Interfaces located in one row it insert add row"""
                contexts[-1]["Interfaces"] = contexts[-1]["Interfaces"] + row[0]
                if row[0][-1] == ",":
                    nextinterface = True
                    continue
                nextinterface = False
                continue
            contexts.append(dict(zip(headline, row)))
            if contexts[-1]["Interfaces"][-1] == ",":
                """If last symbol Interfaces is comma - next row
                consist only Interfaces"""
                nextinterface = True

        complete_config = [self.get_config("system:running-config")]
        for c in contexts:
            """Get configs for context"""
            config = self.get_config(c["URL"])
            complete_config.append(f"!{SEP}{c['ContextName']}{SEP}\n{config}\n")
        return "".join(complete_config)
