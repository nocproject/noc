# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Obsolete data cleanup and system maintainance
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
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
