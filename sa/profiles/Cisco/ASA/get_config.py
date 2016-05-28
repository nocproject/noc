# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
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
                header = []
                head = True
                for l in v.splitlines():
                    l = l.strip()
                    if l == '':
                        continue
                    if head:
                        header = l.split()
                        header[0] = header[0] + header.pop(1)
                        head = False
                        continue
                    row = l.split()
                    if row[0] == "Total":
                        continue
                    contexts.append(dict(zip(header, row)))

                complete_config = self.get_config("system:running-config")
                for c in contexts:
                    # config = self.get_config("system:running-config")
                    config = self.get_config(c["URL"])
                    complete_config += "!{0}{1}{2}\n{3}\n".format("=" * 40, c["ContextName"], "=" * 40, config)
                return complete_config
        else:
            config = self.cli("more system:running-config")
            config = self.strip_first_lines(config, 3)
            return self.cleaned_config(config)
