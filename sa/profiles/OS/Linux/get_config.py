# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import noc.sa.script
## NOC modules
from noc.sa.interfaces import IGetConfig


class Script(noc.sa.script.Script):
    name = "OS.Linux.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = ''
        for i in self.attrs:
            if i.startswith('config'):
                files = {}
                files['name'] = self.attrs[i]
                conf = str(self.cli("/bin/cat " + str(self.attrs[i])))
                files['config'] = conf
                config.append(files)
        if not config:
            config = self.cli("cat /tmp/system.cfg 2>/dev/null")
        if not config:
            cmd = "for i in `du -a /etc/ 2>/dev/null |awk '{print $2}' "
            cmd += "2>/dev/null`; do echo ''; echo $i; if [ -f $i ];"
            cmd += "then cat $i; fi; done"
            config = self.cli(cmd)
        if not config:
            raise Exception("Not implemented")
        config = self.cleaned_config(config)
        if self.encoding:
            config = unicode(config, self.encoding).encode("utf8", "ignore")
        return config
