# ---------------------------------------------------------------------
# ObjectStatus
# Updated by SAE according to ping check changes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator
from threading import Lock
from typing import List, Dict, Tuple, Optional, Set

# Third-party modules
import cachetools
from mongoengine.document import Document
from mongoengine.fields import IntField, BooleanField, DateTimeField
from pymongo import UpdateOne

# NOC modules
from noc.core.service.loader import get_service
from noc.fm.models.outage import Outage
from noc.config import config

id_lock = Lock()


class ObjectStatus(Document):
    meta = {
        "collection": "noc.cache.object_status",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["object"],
    }
    # Object id
    object = IntField(required=True, unique=True)
    # True - object is Up
    # False - object is Down
    status = BooleanField()
    # Last update
    last = DateTimeField()

    _failed_object_cache = cachetools.TTLCache(
        maxsize=10, ttl=config.discovery.object_status_cache_ttl
    )

    def __str__(self):
        return f"{self.object}: {self.status}"

    @classmethod
    def get_status(cls, object) -> bool:
        d = ObjectStatus._get_collection().find_one({"object": object.id})
        if d:
            return d["status"]
        return True

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_failed_object_cache"), lock=lambda _: id_lock)
    def get_failed_objects(cls) -> Set[int]:
        r = next(
            ObjectStatus._get_collection().aggregate(
                [
                    {"$match": {"status": False}},
                    {"$group": {"_id": 1, "objects": {"$push": "$object"}}},
                ]
            ),
            None,
        )
        if not r:
            return set()
        return set(r["objects"])

    @classmethod
    def is_failed(cls, oid: int) -> bool:
        """
        Check Object status is failed
        :param oid: Object Id
        """
        return oid in cls.get_failed_objects()

    @classmethod
    def get_last_status(cls, object) -> Tuple[Optional[bool], Optional[datetime.datetime]]:
        """
        Returns last registred status and update time
        :param object: Managed Object id
        :return: last status, last update or None
        """
        d = ObjectStatus._get_collection().find_one({"object": object.id})
        if d:
            return d["status"], d.get("last")
        return None, None

    @classmethod
    def get_statuses(cls, objects: List[int]) -> Dict[int, bool]:
        """
        Returns a map of object id -> status
        for a list od object ids
        """
        s = {}
        c = cls._get_collection()
        while objects:
            chunk, objects = objects[:500], objects[500:]
            for d in c.find({"object": {"$in": chunk}}):
                s[d["object"]] = d["status"]
        return s

    @classmethod
    def set_status(cls, object, status, ts=None):
        """
        Update object status
        :param object: Managed Object instance
        :param status: New status
        :param ts: Status change timestamp
        :return: True, if status has been changed, False - out-of-order update
        """
        ts = ts or datetime.datetime.now()
        coll = ObjectStatus._get_collection()
        # Update naively
        # Must work in most cases
        # find_and_modify returns old document or None for upsert
        r = coll.find_one_and_update(
            {"object": object.id}, update={"$set": {"status": status, "last": ts}}, upsert=True
        )
        if not r:
            # Setting status for first time
            # Work complete
            return True
        if r["last"] > ts:
            # Oops, out-of-order update
            # Restore correct state
            coll.update_one({"object": object.id}, {"status": r["status"], "last": r["last"]})
            return False
        if r["status"] != status:
            # Status changed
            Outage.register_outage(object, not status, ts=ts)
        return True

    @classmethod
    def update_status_bulk(cls, statuses: List[Tuple[int, bool, Optional[int]]]):
        """
        Update statuses bulk
        :param statuses:
        :return:
        """
        from noc.sa.models.managedobject import ManagedObject

        now = datetime.datetime.now()
        coll = ObjectStatus._get_collection()

        bulk = []
        outages: List[Tuple[int, datetime.datetime, datetime.datetime]] = []
        # Getting current status
        cs = {
            x["object"]: {"status": x["status"], "last": x.get("last")}
            for x in coll.find({"object": {"$in": [x[0] for x in statuses]}})
        }
        for oid, status, ts in statuses:
            ts = ts or now
            if oid not in cs or (cs[oid]["status"] != status and cs[oid]["last"] <= ts):
                bulk += [
                    UpdateOne(
                        {"object": oid}, {"$set": {"status": status, "last": ts}}, upsert=True
                    )
                ]
                if status and oid in cs:
                    outages.append((oid, cs[oid]["last"], ts))
                cs[oid] = {"status": status, "last": ts}
            elif oid in cs and cs[oid]["last"] > ts:
                # Oops, out-of-order update
                # Restore correct state
                pass
        if not bulk:
            return
        coll.bulk_write(bulk, ordered=True)
        svc = get_service()
        # Send outages
        for out in outages:
            # Sent outages
            oid, start, stop = out
            mo = ManagedObject.get_by_id(oid)
            svc.register_metrics(
                "outages",
                [
                    {
                        "date": now.date().isoformat(),
                        "ts": now.replace(microsecond=0).isoformat(),
                        "managed_object": mo.bi_id,
                        "start": start.replace(microsecond=0).isoformat(),
                        "stop": stop.replace(microsecond=0).isoformat(),
                        "administrative_domain": mo.administrative_domain.bi_id,
                    }
                ],
                key=mo.bi_id,
            )
