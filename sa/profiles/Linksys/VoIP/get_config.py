# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.VoIP.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig
from noc.lib.text import strip_html_tags


class Script(noc.sa.script.Script):
    name = "Linksys.VoIP.get_config"
    implements = [IGetConfig]

    rx_line = re.compile(
        r"^(Current Time:|Broadcast Bytes|{|}|table|\.|function|var|onLoad|\s+|$)")

    def execute(self):
        conf = self.http.get("/")
        conf = strip_html_tags(conf)
        conf = self.cleaned_config(conf)
        conf = conf.split('\n')
        config = []
        for l in conf:
            match = self.rx_line.match(l)
            if not match:
                config.append(l)
        return '\n'.join(config)
