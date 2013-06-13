# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Send check changed notification
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler import Job


class TouchCheckJob(Job):
    name = "pm.touch_check"
    ignored = False

    def handler(self, *args, **kwargs):
        self.scheduler.daemon.send(
            {
                "check": str(self.key)
            },
            destination="/queue/pm/check/change/"
        )
        return True
