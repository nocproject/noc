# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SelectorCache
# Updated by sa.refresh_selector_cache job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import operator
from threading import Lock
import re
# Third-party modules
from pymongo import ReadPreference, UpdateOne, InsertOne, DeleteOne, WriteConcern
from pymongo.errors import BulkWriteError
from mongoengine.document import Document
from mongoengine.fields import IntField
import cachetools
# NOC modules
from noc.core.defer import call_later

logger = logging.getLogger(__name__)
q_lock = Lock()


class SelectorCache(Document):
    meta = {
        "collection": "noc.cache.selector",
        "strict": False,
        "auto_create_index": False,
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
        return cls.objects.filter(
            object=oid,
            read_preference=ReadPreference.SECONDARY_PREFERRED
        ).values_list("selector")

    @classmethod
    def is_in_selector(cls, object, selector):
        oid = object
        if hasattr(object, "id"):
            oid = object.id
        sid = selector
        if hasattr(selector, "id"):
            sid = selector.id
        return bool(cls._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        ).find_one({
            "object": oid,
            "selector": sid
        }))

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("q_cache"), lock=lambda x: q_lock)
    def get_active_selectors(cls):
        from .managedobjectselector import ManagedObjectSelector
        return list(ManagedObjectSelector.objects.filter(is_enabled=True))

    @classmethod
    def selectors_for_object(cls, object):
        from noc.sa.models.administrativedomain import AdministrativeDomain
        from noc.sa.models.managedobject import ManagedObject
        from django.db import connection
        selectors = cls.get_active_selectors()
        if not selectors:
            return set()
        sql = []
        params = []
        for s in selectors:
            if s.filter_id and object.id != s.filter_id:
                continue
            if s.filter_managed is not None and object.is_managed != s.filter_managed:
                continue
            if s.filter_profile and object.profile.id != s.filter_profile.id:
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
        if not sql:
            # Fully optimized, fully negative
            return set()
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
        collection = SelectorCache._get_collection().with_options(write_concern=WriteConcern(w=0))
        bulk = []
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
                    bulk += [UpdateOne({"_id": sdata["_id"]}, {
                        "$set": {
                            "vc_domain": vcdomain
                        }
                    })]
                del old[s]
            else:
                # New record
                logging.debug(
                    "[%s] Add to selector %s",
                    object.name, s
                )
                bulk += [InsertOne({
                    "object": object.id,
                    "selector": s,
                    "vc_domain": vcdomain
                })]
        # Delete stale records
        for sdata in old.itervalues():
            logging.debug(
                "[%s] Remove from selector %s",
                object.name, sdata["_id"]
            )
            bulk += [DeleteOne({"_id": sdata["_id"]})]
        # Apply changes
        if bulk:
            logging.info("[%s]Commiting changes to database", object.name)
            try:
                r = collection.bulk_write(bulk, ordered=False)
                logging.info("Database has been synced")
                logging.info("Inserted: %d, Modify: %d, Deleted: %d",
                             r.inserted_count + r.upserted_count,
                             r.modified_count, r.deleted_count)
            except BulkWriteError as e:
                logging.error("Bulk write error: '%s'", e.details)
                logging.error("Stopping check")


def refresh():
    """
    Rebuild selector cache job
    """
    def diff(old, new):
        def getnext(g):
            try:
                return next(g)
            except StopIteration:
                return None

        o = getnext(old)
        n = getnext(new)
        while o or n:
            if not o:
                # New
                yield None, n
                n = getnext(new)
            elif not n:
                # Removed
                yield o, None
                o = getnext(old)
            else:
                if n[0] == o[0]:
                    # Changed
                    if n != o[:3]:
                        yield o, n
                    n = getnext(new)
                    o = getnext(old)
                elif n[0] < o[0]:
                    # Added
                    yield None, n
                    n = getnext(new)
                else:
                    # Removed
                    yield o, None
                    o = getnext(old)

    from .managedobjectselector import ManagedObjectSelector

    r = []
    logger.info("Building selector cache")
    logger.info("Loading existing cache")
    old = sorted(
        (d["object"], d["selector"], d.get("vc_domain"), d["_id"])
        for d in SelectorCache._get_collection().find({})
    )
    logger.info("Generating new selector cache")
    new = []
    for s in ManagedObjectSelector.objects.filter(is_enabled=True):
        sid = s.id
        new += [
            (r[0], sid, r[1])
            for r in s.managed_objects.values_list("id", "vc_domain")
        ]
    new = sorted(new)
    logger.info("Merging selector caches")
    n_new = 0
    n_changed = 0
    n_removed = 0
    collection = SelectorCache._get_collection()
    bulk = []
    for o, n in diff(iter(old), iter(new)):
        if o is None:
            # New
            bulk += [InsertOne({
                "object": n[0], "selector": n[1], "vc_domain": n[2]
            })]
            n_new += 1
        elif n is None:
            # Removed
            bulk += [DeleteOne({"_id": o[-1]})]
            n_removed += 1
        else:
            # Changed
            bulk += [UpdateOne({"_id": o[-1]}, {
                "$set": {
                    "object": n[0], "selector": n[1], "vc_domain": n[2]
                }
            })]
            n_changed += 1
    if n_new + n_changed + n_removed:
        logger.info("Writing (new=%s, changed=%s, removed=%s)",
                    n_new, n_changed, n_removed)
        if bulk:
            logger.info("Commiting changes to database")
            try:
                r = collection.bulk_write(bulk, ordered=False)
                logger.info("Database has been synced")
                logger.info("Inserted: %d, Modify: %d, Deleted: %d",
                             r.inserted_count + r.upserted_count,
                             r.modified_count, r.deleted_count)
            except BulkWriteError as e:
                logger.error("Bulk write error: '%s'", e.details)
                logger.error("Stopping check")
    logger.info("Done ")
    return
