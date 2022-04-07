# ---------------------------------------------------------------------
# ManagedObjectData
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
import logging
from typing import Dict, List, Set, Iterable
from dataclasses import dataclass

# Third-party modules
import bson
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
from mongoengine.document import Document
from mongoengine.fields import IntField, ListField, ObjectIdField
import cachetools
from django.db import connection as pg_connection


@dataclass(frozen=True)
class ObjectUplinks(object):
    object_id: int
    uplinks: List[int]
    rca_neighbors: List[int]


id_lock = Lock()
neighbor_lock = Lock()

logger = logging.getLogger(__name__)


class ObjectData(Document):
    meta = {
        "collection": "noc.objectdata",
        "indexes": ["uplinks"],
        "strict": False,
        "auto_create_index": False,
    }
    object = IntField(primary_key=True)
    # Uplinks
    uplinks = ListField(IntField())
    # RCA neighbors cache
    rca_neighbors = ListField(IntField())
    # xRCA donwlink merge window settings
    # for rca_neighbors.
    # Each position represents downlink merge windows for each rca neighbor.
    # Windows are in seconds, 0 - downlink merge is disabled
    dlm_windows = ListField(IntField())
    # Paths
    adm_path = ListField(IntField())
    segment_path = ListField(ObjectIdField())
    container_path = ListField(ObjectIdField())

    _id_cache = cachetools.TTLCache(10000, ttl=120)
    _neighbor_cache = cachetools.TTLCache(1000, ttl=300)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def _get_by_id(cls, object_id):
        return ObjectData.objects.filter(object=object_id).first()

    @classmethod
    def get_by_id(cls, object):
        if isinstance(object, bson.ObjectId):
            # For tests supported
            return None
        if hasattr(object, "id"):
            object = object.id
        return cls._get_by_id(object)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_neighbor_cache"), lock=lambda _: neighbor_lock)
    def _get_neighbors(cls, object_id):
        n = set()
        for d in ObjectData._get_collection().find({"uplinks": object_id}, {"_id": 1}):
            n.add(d["_id"])
        return list(n)

    @classmethod
    def get_neighbors(cls, object):
        if hasattr(object, "id"):
            object = object.id
        return cls._get_neighbors(object)

    @classmethod
    def uplinks_for_objects(cls, objects):
        """
        Returns uplinks for list of objects
        :param objects: List of object
        :return: dict of object id -> uplinks
        """
        o = []
        for obj in objects:
            if hasattr(obj, "id"):
                obj = obj.id
            o += [obj]
        uplinks = {obj: [] for obj in o}
        for d in ObjectData._get_collection().find({"_id": {"$in": o}}, {"_id": 1, "uplinks": 1}):
            uplinks[d["_id"]] = d.get("uplinks", [])
        return uplinks

    @classmethod
    def update_uplinks(cls, iter_uplinks: Iterable[ObjectUplinks]) -> None:
        """
        Update ObjectUplinks in database
        :param uplinks: Iterable of ObjectUplinks
        :return:
        """
        obj_data: List[ObjectUplinks] = []
        seen_neighbors: Set[int] = set()
        uplinks: Dict[int, Set[int]] = {}
        for ou in iter_uplinks:
            obj_data += [ou]
            seen_neighbors |= set(ou.rca_neighbors)
            uplinks[ou.object_id] = set(ou.uplinks)
        if not obj_data:
            return  # No uplinks for segment
        # Get downlink_merge window settings
        dlm_settings: Dict[int, int] = {}
        if seen_neighbors:
            with pg_connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT mo.id, mop.enable_rca_downlink_merge, mop.rca_downlink_merge_window
                    FROM sa_managedobject mo JOIN sa_managedobjectprofile mop
                        ON mo.object_profile_id = mop.id
                    WHERE mo.id IN %s""",
                    [tuple(seen_neighbors)],
                )
                dlm_settings = {mo_id: dlm_w for mo_id, is_enabled, dlm_w in cursor if is_enabled}
        # Propagate downlink-merge settings downwards
        dlm_windows: Dict[int, int] = {}
        MAX_WINDOW = 1000000
        for o in seen_neighbors:
            ups = uplinks.get(o)
            if not ups:
                continue
            w = min(dlm_settings.get(u, MAX_WINDOW) for u in ups)
            if w == MAX_WINDOW:
                w = 0
            dlm_windows[o] = w
        # Prepare bulk update operation
        bulk = [
            UpdateOne(
                {"_id": ou.object_id},
                {
                    "$set": {
                        "uplinks": ou.uplinks,
                        "rca_neighbors": ou.rca_neighbors,
                        "dlm_windows": [dlm_windows.get(o, 0) for o in ou.rca_neighbors],
                    }
                },
                upsert=True,
            )
            for ou in obj_data
        ]
        try:
            ObjectData._get_collection().bulk_write(bulk, ordered=False)
        except BulkWriteError as e:
            logger.error("Bulk write error: '%s'", e.details)

    @classmethod
    def refresh_path(cls, obj):
        ObjectData._get_collection().update(
            {"_id": obj.id},
            {
                "$set": {
                    "adm_path": obj.administrative_domain.get_path(),
                    "segment_path": obj.segment.get_path(),
                    "container_path": obj.container.get_path() if obj.container else [],
                }
            },
            upsert=True,
        )
