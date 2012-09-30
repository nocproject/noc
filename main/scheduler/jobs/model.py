# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Model Maintainance Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import random
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob


class ModelJob(IntervalJob):
    ignored = True
    initial_submit_interval = None
    initial_submit_concurrency = None
    success_retry = None
    failed_retry = None

    @classmethod
    def can_submit(cls, object):
        """
        Check object is submittable
        :param cls:
        :param object:
        :return:
        """
        return True

    @classmethod
    def initial_submit(cls, scheduler, keys):
        now = datetime.datetime.now()
        isc = cls.initial_submit_concurrency
        for o in cls.model.objects.exclude(id__in=keys).only("id"):
            if cls.can_submit(o):
                cls.submit(
                    scheduler=scheduler,
                    key=o.id,
                    interval=cls.success_retry,
                    failed_interval=cls.failed_retry,
                    randomize=True,
                    ts=now + datetime.timedelta(
                        seconds=random.random() * cls.initial_submit_interval))
                isc -= 1
                if not isc:
                    break

    def send(self, message, destination,
             receipt=False, persistent=False):
        self.scheduler.daemon.send(message, destination,
            receipt=receipt, persistent=persistent)
