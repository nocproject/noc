# -*- coding: utf-8 -*-
__author__ = 'FeNikS'
# Python modules
# NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name = "Sencore.Probe.get_config"
    implements = [IGetConfig]

    suffixes = ["/probe/status",
                "/probe/generaldata?&&",
                "/probe/etrdata?&&"
                 ]

    def execute(self):        
        result = ["<?xml version=\"1.0\"?>\n<Root>"]

        for suffix in self.suffixes:
            data = self.http.get(suffix)
            data = data.replace("<?xml version=\"1.0\"?>", "")
            result.append(data)
        result.append("</Root>")
        config = "\n".join(result)

        return self.cleaned_config(config)