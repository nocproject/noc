# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SelectorCache
## Updated by sa.refresh_selector_cache job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import Document, IntField
from noc.lib.scheduler.utils import sliding_job


class SelectorCache(Document):
    meta = {
        "collection": "noc.cache.selector",
        "allow_inheritance": False,
        "indexes": ["object", "selector", "vc_domain"]
    }
    object = IntField(required=True)
    selector = IntField(required=False)
    vc_domain = IntField(required=False)

    def __unicode__(self):
        return "%s:%s" % (self.object, self.selector)

    @classmethod
    def refresh(cls):
        sliding_job("main.jobs", "sa.refresh_selector_cache", delta=5)

    @classmethod
    def get_object_selectors(cls, object):
        oid = object
        if hasattr(object, "id"):
            oid = object.id
        return cls.objects.filter(object=oid).values_list("selector")

    @classmethod
    def rebuild_for_object(cls, object):
        # Remove old data
        cls.objects.filter(object=object.id).delete()
        #
        r = []
        for s in ManagedObjectSelector.objects.filter(is_enabled=True):
            for o in s.managed_objects:
                d = o.vc_domain.id if o.vc_domain else None
                r += [
                    {
                        "object": o.id,
                        "selector": s.id,
                        "vc_domain": d
                    }
                ]
        cls._get_collection().insert(r)

##
from managedobjectselector import ManagedObjectSelector