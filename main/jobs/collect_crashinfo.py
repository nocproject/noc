# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import new crashinfo
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.support.models.crashinfo import Crashinfo


class CollectCrashinfoJob(AutoIntervalJob):
    name = "main.collect_crashinfo"
    interval = 60
    randomize = True

    def handler(self, *args, **kwargs):
        Crashinfo.scan()
        return True
