# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_config"
    implements = [IGetConfig]
    rx_not_found = re.compile(r"^cat:.+?No (?:match|such file or directory)")
    configs = ["/etc/rc.conf", "/etc/rc.conf.d/*",
        "/usr/local/etc/rc.conf.d/*", "/etc/rc.local"]

    def execute(self):
        config = ""
        for c in self.configs:
            conf = self.cli("cat -v %s ; echo" % c)
            match = self.rx_not_found.search(conf)
            if not match:
                config = config + ("\n## %s\n" % c) + conf

        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
