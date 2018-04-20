# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm trigger
##----------------------------------------------------------------------
## Copyright (C) 2007-2012, The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.nosql import ObjectId


class JobLauncher(object):
    def __init__(self, scheduler, job_name, interval, vars):
        self.scheduler = scheduler
        self.job = scheduler.get_job_class(job_name)
        self.interval = interval
        x = []
        for k in vars:
            x += ["'%s': %s" % (k, vars[k])]
        self.vars_expr = compile("{%s}" % ", ".join(x),
            "<string>", "eval")

    def get_vars(self, alarm):
        """
        Calculate job vars
        :param alarm:
        :return:
        """
        return eval(self.vars_expr, {}, {
            "alarm": alarm,
            "datetime": datetime,
            "ObjectId": ObjectId
        })

    def submit(self, alarm):
        cfg = {
            "data": self.get_vars(alarm),
            "interval": self.interval,
            "failed_interval": None,
            "keep_offset": True
        }
        cfg.update(self.job.get_job_config(alarm, cfg))
        self.job.submit(
            self.scheduler,
            key=alarm.id,
            **cfg
        )
