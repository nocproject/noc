# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.ASA.get_config"
    interface = IGetConfig

    context_line = re.compile(r".*?(?P<contextname>\S+)\s+(?P<class>\S+)\s+(?P<interfaces>\S+)\s+(?P<url>.+)",
                              re.MULTILINE | re.DOTALL)

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
                for l in v.splitlines():
                    l = l.strip()
                    if l == '':
                        continue
                    match = self.re_search(self.context_line, l)
                    if match.group("contextname") == "Context" or match.group("contextname") == "Total":
                        continue
                    contexts.append({"name": match.group("contextname"),
                                    "url": match.group("url")})

                complete_config = self.get_config("system:running-config")
                for c in contexts:
                    # config = self.get_config("system:running-config")
                    config = self.get_config(c["url"])
                    complete_config += "!{0}{1}{2}\n{3}\n".format("=" * 40, c["name"], "=" * 40, config)
                return complete_config
        else:
            config = self.cli("more system:running-config")
            config = self.strip_first_lines(config, 3)
            return self.cleaned_config(config)
