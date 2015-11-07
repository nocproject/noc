# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SelectorCache
## Updated by sa.refresh_selector_cache job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.lib.nosql import Document, IntField
from noc.core.defer import call_later

logger = logging.getLogger(__name__)


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
        call_later(
            "noc.sa.models.selectorcache.refresh",
            delay=10
        )

    @classmethod
    def get_object_selectors(cls, object):
        oid = object
        if hasattr(object, "id"):
            oid = object.id
        return cls.objects.filter(object=oid).values_list("selector")

    @classmethod
    def rebuild_for_object(cls, object):
        from managedobjectselector import ManagedObjectSelector
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
        if r:
            cls._get_collection().insert(r)


def refresh():
    """
    Rebuild selector cache job
    """
    from managedobjectselector import ManagedObjectSelector

    r = []
    logger.info("Building selector cache")
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
    # Write temporary cache
    if r:
        logger.info("Writing cache")
        cache = SelectorCache._get_collection_name()
        c = SelectorCache._get_db()[cache + ".tmp"]
        c.insert(r)
        # Substitute cache
        c.rename(cache, dropTarget=True)
    else:
        # No data
        logger.info("No data to write")
