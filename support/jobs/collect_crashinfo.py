# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Import new crashinfo
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Import new crashinfo
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.support.models.crashinfo import Crashinfo


class CollectCrashinfoJob(AutoIntervalJob):
    name = "support.collect_crashinfo"
    interval = 60
    randomize = True

    def handler(self, *args, **kwargs):
        Crashinfo.scan()
        return True
