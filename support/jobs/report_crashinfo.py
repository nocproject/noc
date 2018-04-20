# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Obsolete data cleanup and system maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Obsolete data cleanup and system maintainance
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.support.models.crashinfo import Crashinfo
from noc.support.cp import CPClient


class ReportCrashinfoJob(AutoIntervalJob):
    name = "support.report_crashinfo"
    interval = 60
    randomize = True

    def handler(self, *args, **kwargs):
        for ci in Crashinfo.objects.filter(status="r"):
            try:
                ci.report()
            except CPClient, why:
                self.logger.error("Failed to report crashinfo %s: %s",
                                  ci.uuid, why)
        return True
