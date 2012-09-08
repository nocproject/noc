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
    def initial_submit(cls, scheduler, keys):
        now = datetime.datetime.now()
        profiles = [s.rsplit(".", 1)[0]
                    for s in script_registry.classes
                    if s.endswith(".%s" % cls.map_task)]
        for mo in ManagedObject.objects.filter(
            is_managed=True, profile_name__in=profiles).exclude(
            id__in=keys).only("id")[:cls.initial_submit_concurrency]:
            cls.submit(
                scheduler=scheduler, key=mo.id,
                interval=cls.success_retry,
                failed_interval=cls.failed_retry,
                randomize=True,
                ts=now + datetime.timedelta(seconds=random.random() * cls.initial_submit_interval))

    def get_defererence_query(self):
        """
        Restrict job to objects having *is_managed* set
        :return:
        """
        return {"id": self.key, "is_managed": True}
