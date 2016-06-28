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
    def is_in_selector(cls, object, selector):
        oid = object
        if hasattr(object, "id"):
            oid = object.id
        sid = selector
        if hasattr(selector, "id"):
            sid = selector.id
        return bool(cls._get_collection().find_one({
            "object": oid,
            "selector": sid
        }))

    @classmethod
    def rebuild_for_object(cls, object):
        from managedobjectselector import ManagedObjectSelector
        from managedobject import ManagedObject
        # Stored data
        old = {}  # selector -> doc
        for d in SelectorCache._get_collection().find({"object": object.id}):
            old[d["selector"]] = d
        # Refreshed data
        vcdomain = object.vc_domain.id if object.vc_domain else None
        bulk = SelectorCache._get_collection().initialize_unordered_bulk_op()
        nb = 0
        for s in ManagedObjectSelector.objects.filter(is_enabled=True):
            if ManagedObject.objects.filter(id=object.id).filter(s.Q).exists():
                sdata = old.get(s.id)
                if sdata:
                    # Cache record exists
                    if sdata.get("vc_domain") != vcdomain:
                        # VC Domain changed
                        logger.debug(
                            "[%s] Changing VC Domain to %s",
                            object.name,
                            vcdomain
                        )
                        bulk.find({"_id": sdata["_id"]}).update({
                            "vc_domain": vcdomain
                        })
                        nb += 1
                    del old[s.id]
                else:
                    # New record
                    logging.debug(
                        "[%s] Add to selector %s",
                        object.name, s.name
                    )
                    bulk.insert({
                        "object": object.id,
                        "selector": s.id,
                        "vc_domain": vcdomain
                    })
                    nb += 1
        # Delete stale records
        for sdata in old.itervalues():
            logging.debug(
                "[%s] Remove from selector %s",
                object.name, sdata["_id"]
            )
            bulk.find({"_id": sdata["_id"]}).remove()
        # Apply changes
        if nb:
            logging.debug(
                "[%s] Committing %d changes",
                object.name, nb
            )
            bulk.execute({"w": 0})


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
