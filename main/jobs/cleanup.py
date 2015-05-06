# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Obsolete data cleanup and system maintainance
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
from mongoengine.django.sessions import MongoSession
## NOC modules
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.sa.models import ReduceTask, MapTask
from noc.lib.db import vacuum
from noc.sa.models.failedscriptlog import FailedScriptLog


class CleanupJob(AutoIntervalJob):
    name = "main.cleanup"
    interval = 3600
    randomize = True

    def cleanup_mrt(self):
        """
        Remove old map/reduce tasks
        """
        self.info("Cleanup map/reduce tasks")
        watermark = datetime.datetime.now() - datetime.timedelta(days=1)
        for t in ReduceTask.objects.filter(stop_time__lt=watermark):
            MapTask.objects.filter(task=t).delete()
            t.delete()
        self.info("Map/Reduce tasks are cleaned")
        self.info("Compacting MRT tables")
        vacuum(ReduceTask._meta.db_table, analyze=True)
        vacuum(MapTask._meta.db_table, analyze=True)
        self.info("MRT Tables are compacted")

    def cleanup_empty_categories(self):
        """
        Cleanup empty categories
        """
        from noc.fm.models import AlarmClass, AlarmClassCategory,\
            EventClass, EventClassCategory, EventClassificationRule,\
            EventClassificationRuleCategory
        
        self.info("Cleaning empty categories")
        for cls, cat_cls in [(AlarmClass, AlarmClassCategory),
                             (EventClass, EventClassCategory),
                             (EventClassificationRule,
                              EventClassificationRuleCategory)]:
            
            for cat in cat_cls.objects.all().order_by("-name"):
                if cls.objects.filter(category=cat.id).count():
                    # There are child items
                    continue
                if cat_cls.objects.filter(parent=cat.id).count():
                    # There are
                    continue
                self.info("Cleaning %s category: %s" % (cls, cat))
                cat.delete()
        self.info("Empty categories are cleaned")

    def handler(self, *args, **kwargs):
        self.cleanup_mrt()
        self.cleanup_empty_categories()
        return True
