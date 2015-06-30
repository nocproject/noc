# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DiscoveryJob
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime
import random
## Django modules
from django.db.models.signals import post_save, pre_delete
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, StringField, IntField, DynamicField, FloatField
## NOC modules
from noc.inv.discovery.utils import get_active_discovery_methods
from noc.lib.scheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)


class DiscoveryJob(Document):
    meta = {
        "collection": "noc.schedules.inv.discovery"
    }
    ts = DateTimeField()
    jcls = StringField()
    status = StringField(db_field="s")
    object = IntField(db_field="key")
    data = DynamicField()
    schedule = DynamicField()
    last = DateTimeField()
    last_status = StringField(db_field="ls")
    last_duration = FloatField(db_field="ldur")
    last_success = DateTimeField(db_field="st")
    runs = IntField(db_field="runs")
    tb = StringField(db_field="tb")
    log = StringField()
    faults = IntField()

    def __unicode__(self):
        return "%s %s" % (self.jcls, self.object)

    @classmethod
    def install(cls):
        logger.info("Installing discovery jobs watchers")
        from noc.sa.models.managedobject import ManagedObject
        from noc.sa.models.managedobjectprofile import ManagedObjectProfile
        post_save.connect(cls.on_managed_object_save, sender=ManagedObject)
        pre_delete.connect(cls.on_managed_object_delete, sender=ManagedObject)
        post_save.connect(cls.on_objectprofile_save, sender=ManagedObjectProfile)
        pre_delete.connect(cls.on_objectprofile_delete, sender=ManagedObjectProfile)

    @classmethod
    def on_managed_object_save(cls, sender, instance, created,
                               *args, **kwargs):
        cls.apply_object_jobs(instance)

    @classmethod
    def on_managed_object_delete(cls, sender, instance, *args, **kwargs):
        cls.delete_object_jobs(instance)

    @classmethod
    def on_objectprofile_save(cls, sender, instance, created, *args,
                              **kwargs):
        cls.apply_objectprofile_jobs(instance)

    @classmethod
    def on_objectprofile_delete(cls, sender, instance, *args, **kwargs):
        cls.delete_objectprofile_jobs(instance)

    @classmethod
    def apply_object_jobs(cls, object):
        """
        Apply discovery jobs to object
        """
        methods = get_active_discovery_methods()
        # Get current schedules
        current = {}  # name -> (interval, failed interval)
        for d in cls._get_collection().find({
            "key": object.id,
            "jcls": {
                "$in": methods
            }
        }, {"jcls": 1, "schedule": 1}):
            current[d["jcls"]] = (d["schedule"]["interval"],
                                  d["schedule"].get("failed_interval"))
        # Get effective schedules
        bulk = cls._get_collection().initialize_unordered_bulk_op()
        n = 0
        p = object.object_profile
        now = datetime.datetime.now()
        for m in methods:
            if not getattr(p, "enable_%s" % m):
                continue
            interval = (
                getattr(p, "%s_max_interval" % m),
                getattr(p, "%s_min_interval" % m)
            )
            if m in current:
                if current[m] != interval:
                    # Change schedule
                    logger.debug("[%s] changing %s interval %s -> %s",
                                 object.name, m, current[m], interval)
                    bulk.find({"key": object.id, "jcls": m}).update({
                        "$set": {
                            "schedule.interval": interval[0],
                            "schedule.failed_interval": interval[1]
                        }
                    })
                    n += 1
            else:
                # Create schedule
                logger.debug("[%s] creating schedule for %s",
                             object.name, m)
                bulk.insert({
                    "jcls": m,
                    "key": object.id,
                    "s": "W",
                    "data": None,
                    "ts": now,
                    "schedule": {
                        "interval": interval[0],
                        "failed_interval": interval[1],
                        "offset": random.random()
                    }
                })
                n += 1
        # Delete stale schedules
        stale = set(current) - set(methods)
        if stale:
            logger.debug("[%s] deleting stale schedules: %s",
                         object.name, ", ".join(stale))
            bulk.find({
                "key": object.id,
                "$jcls": {
                    "$in": list(stale)
                }
            }).remove()
            n += 1
        if n:
            logger.debug("Bulk update schedule")
            bulk.execute({"w": 0})

    @classmethod
    def delete_object_jobs(cls, object):
        logger.debug("[%s] deleting object jobs", object.name)
        cls._get_collection().remove({
            "key": object.id
        })

    @classmethod
    def apply_objectprofile_jobs(cls, profile):
        """
        Apply discovery jobs to all objects
        """
        object_ids = list(profile.managedobject_set.values_list("id", flat=True))
        if not object_ids:
            return
        methods = get_active_discovery_methods()
        current = {}  # object, method -> (interval, failed interval)
        for d in cls._get_collection().find({
            "key": {
                "$in": object_ids
            },
            "jcls": {
                "$in": methods
            }
        }, {"jcls": 1, "key": 1, "schedule": 1}):
            current[(d["key"], d["jcls"])] = (
                d["schedule"]["interval"],
                d["schedule"].get("failed_interval")
            )
        # Get effective capabilities
        bulk = cls._get_collection().initialize_unordered_bulk_op()
        n = 0
        now = datetime.datetime.now()
        for m in methods:
            if not getattr(profile, "enable_%s" % m):
                continue
            interval = (
                getattr(profile, "%s_max_interval" % m),
                getattr(profile, "%s_min_interval" % m)
            )
            for obj in object_ids:
                if (obj, m) in current:
                    if current[(obj, m)] != interval:
                        # Change schedule
                        logger.debug("[%s] changing %s interval %s -> %s",
                                     obj, m, current[(obj, m)], interval)
                        bulk.find({"key": obj, "jcls": m}).update({
                            "$set": {
                                "schedule.interval": interval[0],
                                "schedule.failed_interval": interval[1]
                            }
                        })
                        n += 1
                    del current[(obj, m)]
                else:
                    # Create schedule
                    logger.debug("[%s] creating schedule for %s",
                                 obj, m)
                    bulk.insert({
                        "jcls": m,
                        "key": obj,
                        "s": "W",
                        "data": None,
                        "ts": now,
                        "schedule": {
                            "interval": interval[0],
                            "failed_interval": interval[1],
                            "offset": random.random()
                        }
                    })
                    n += 1
        # Delete stale schedules
        for obj, m in current:
            logger.debug("[%s] deleting stale schedule: %s", obj, m)
            bulk.find({
                "key": obj,
                "jcls": m
            }).remove()
            n += 1
        if n:
            logger.debug("Bulk update schedule")
            bulk.execute({"w": 0})

    @classmethod
    def delete_objectprofile_jobs(cls, profile):
        object_ids = list(profile.managedobject_set.values_list("id", flat=True))
        if not object_ids:
            return
        methods = get_active_discovery_methods()
        bulk = cls._get_collection().initialize_unordered_bulk_op()
        for m in methods:
            logger.debug("[%s] Deleting stale schedules for %s",
                         profile.name, m)
            bulk.find({
                "jcls": m,
                "key": {
                    "$in": object_ids
                }
            })
        bulk.execute({"w": 0})

    @classmethod
    def set_deferred(cls, object):
        logger.debug("Setting deferred discovery status for %s",
                     object)
        cls._get_collection().update({
            "key": object.id,
            Scheduler.ATTR_STATUS: Scheduler.S_WAIT
        }, {
            "$set": {
                Scheduler.ATTR_STATUS: Scheduler.S_DISABLED
            }
        }, multi=True)

    @classmethod
    def reset_deferred(cls, object):
        logger.debug("Resetting deferred discovery status for %s",
                     object)
        cls._get_collection().update({
            "key": object.id,
            Scheduler.ATTR_STATUS: Scheduler.S_DISABLED
        }, {
            "$set": {
                Scheduler.ATTR_STATUS: Scheduler.S_WAIT
            }
        }, multi=True)

DiscoveryJob.install()
