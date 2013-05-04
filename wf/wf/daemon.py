## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-wf daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from scheduler import WFScheduler
from noc.lib.daemon import Daemon


class WFDaemon(Daemon):
    daemon_name = "noc-wf"

    def __init__(self, *args, **kwargs):
        super(WFDaemon, self).__init__(*args, **kwargs)
        self.scheduler = WFScheduler(self)

    def run(self):
        self.scheduler.run()
