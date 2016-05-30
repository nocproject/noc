# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.ASA.get_config"
    interface = IGetConfig

    def get_config(self, path):
        config = self.cli("more " + path)
        config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)

    def execute(self):
        if self.capabilities.get("Cisco | ASA | Security | Context | Mode"):
            if self.capabilities["Cisco | ASA | Security | Context | Mode"] == "multiple":
                self.cli("changeto system")
                v = self.cli("show context")
                contexts = []
                headline = []
                firsthead = True
                nextinterface = False
                for l in v.splitlines():
                    l = l.strip()
                    if l == '':
                        continue
                    if firsthead:
                        headline = l.split()
                        headline[0] = headline[0] + headline.pop(1)
                        firsthead = False
                        continue
                    row = l.split()
                    if row[0] == "Total":
                        """Skip last row (number of context)"""
                        continue
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

                complete_config = self.get_config("system:running-config")
                for c in contexts:
                    """Get configs for context"""
                    config = self.get_config(c["URL"])
                    complete_config += "!{0}{1}{2}\n{3}\n".format("=" * 40, c["ContextName"], "=" * 40, config)
                return complete_config
        else:
            config = self.cli("more system:running-config")
            config = self.strip_first_lines(config, 3)
            return self.cleaned_config(config)
