# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SelectorCache
## Updated by sa.refresh_selector_cache job
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import operator
from threading import Lock
import re
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField
import cachetools
## NOC modules
from noc.core.defer import call_later

logger = logging.getLogger(__name__)
q_lock = Lock()


class SelectorCache(Document):
    meta = {
        "collection": "noc.cache.selector",
        "allow_inheritance": False,
        "indexes": ["object", "selector", "vc_domain"]
    }
    object = IntField(required=True)
    selector = IntField(required=False)
    vc_domain = IntField(required=False)

    q_cache = cachetools.TTLCache(maxsize=1, ttl=60)

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
    @cachetools.cachedmethod(operator.attrgetter("q_cache"), lock=lambda x: q_lock)
    def get_active_selectors(cls):
        from managedobjectselector import ManagedObjectSelector
        return list(ManagedObjectSelector.objects.filter(is_enabled=True))

    @classmethod
    def selectors_for_object(cls, object):
        from noc.sa.models.administrativedomain import AdministrativeDomain
        from noc.sa.models.managedobject import ManagedObject
        from django.db import connection
        selectors = cls.get_active_selectors()
        if not selectors:
            return []
        sql = []
        params = []
        for s in selectors:
            if s.filter_id and object.id != s.filter_id:
                continue
            if s.filter_managed is not None and object.is_managed != s.filter_managed:
                continue
            if s.filter_profile and object.profile_name != s.filter_profile:
                continue
            if s.filter_pool and object.pool.id != s.filter_pool.id:
                continue
            if (
                s.filter_administrative_domain and
                object.administrative_domain.id not in AdministrativeDomain.get_nested_ids(s.filter_administrative_domain.id)
            ):
                continue
            if s.filter_name:
                try:
                    if not re.search(s.filter_name, object.name):
                        continue
                except re.error:
                    pass
            q = ManagedObject.objects.filter(
                s.Q,
                id=object.id
            ).extra(select={"selector": s.id}).values_list("selector")
            t, p = q.query.sql_with_params()
            sql += [t.rsplit(" ORDER BY ", 1)[0]]
            params += p
        sql = " UNION ALL ".join(sql)
        sql = """
            WITH sa_managedobject_item AS (
              SELECT *
              FROM sa_managedobject
              WHERE id = %d
            )
        """ % object.id + sql.replace(
            "\"sa_managedobject\"",
            "\"sa_managedobject_item\""
        )
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return set(row[0] for row in cursor)

    @classmethod
    def rebuild_for_object(cls, object):
        # Stored data
        old = {}  # selector -> doc
        for d in SelectorCache._get_collection().find({"object": object.id}):
            old[d["selector"]] = d
        # Refreshed data
        vcdomain = object.vc_domain.id if object.vc_domain else None
        bulk = SelectorCache._get_collection().initialize_unordered_bulk_op()
        nb = 0
        for s in cls.selectors_for_object(object):
            sdata = old.get(s)
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
                del old[s]
            else:
                # New record
                logging.debug(
                    "[%s] Add to selector %s",
                    object.name, s
                )
                bulk.insert({
                    "object": object.id,
                    "selector": s,
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
