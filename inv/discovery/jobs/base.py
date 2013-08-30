## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic Managed Object-based discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import random
## Django modules
from django.db.models import Q
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob
from noc.sa.models.managedobject import ManagedObject
from noc.sa.script import script_registry


class MODiscoveryJob(IntervalJob):
    ignored = True
    initial_submit_interval = None
    initial_submit_concurrency = None

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
        qs = cls.initial_submit_queryset()
        if type(qs) == dict:
            qs = Q(**qs)
        for mo in ManagedObject.objects.filter(
            is_managed=True, profile_name__in=profiles).filter(qs).exclude(
            id__in=keys).only("id"):
            if cls.can_submit(mo):
                s_interval = cls.get_submit_interval(mo)
                cls.submit(
                    scheduler=scheduler, key=mo.id,
                    interval=s_interval,
                    failed_interval=s_interval,
                    randomize=True,
                    ts=now + datetime.timedelta(
                        seconds=random.random() * cls.initial_submit_interval))
                isc -= 1
                if not isc:
                    break

    @classmethod
    def initial_submit_queryset(cls):
        """
        Return dict or Q object to restrict intial submit queryset
        :param cls:
        :return:
        """
        return Q()

    def get_defererence_query(self):
        """
        Restrict job to objects having *is_managed* set
        :return:
        """
        return {"id": self.key, "is_managed": True}

    def can_run(self):
        return self.object.get_status() and (
            not self.map_task or self.object.is_managed)

    @classmethod
    def get_submit_interval(cls, object):
        raise NotImplementedError

    def get_interval(self):
        return self.get_submit_interval(self.object)

    def get_group(self):
        return "discovery-%s" % self.key