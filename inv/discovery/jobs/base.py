## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic Managed Object-based discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import random
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob
from noc.sa.models.managedobject import ManagedObject
from noc.sa.script import script_registry


class MODiscoveryJob(IntervalJob):
    ignored = True
    initial_submit_interval = None
    initial_submit_concurrency = None
    success_retry = None
    failed_retry = None

    def get_display_key(self):
        if self.object:
            return self.object.name
        else:
            return self.key

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
        profiles = [s.rsplit(".", 1)[0]
                    for s in script_registry.classes
                    if s.endswith(".%s" % cls.map_task)]
        isc = cls.initial_submit_concurrency
        for mo in ManagedObject.objects.filter(
            is_managed=True, profile_name__in=profiles).exclude(
            id__in=keys).only("id"):
            if cls.can_submit(mo):
                cls.submit(
                    scheduler=scheduler, key=mo.id,
                    interval=cls.success_retry,
                    failed_interval=cls.failed_retry,
                    randomize=True,
                    ts=now + datetime.timedelta(
                        seconds=random.random() * cls.initial_submit_interval))
                isc -= 1
                if not isc:
                    break

    def get_defererence_query(self):
        """
        Restrict job to objects having *is_managed* set
        :return:
        """
        return {"id": self.key, "is_managed": True}

    def can_run(self):
        return not self.map_task or self.object.is_managed
