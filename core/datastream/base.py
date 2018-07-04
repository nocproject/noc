# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataStream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import hashlib
# Third-party modules
import ujson
import bson
import bson.errors
import pymongo
import six
import dateutil.parser
import re
# NOC modules
from noc.core.perf import metrics
from noc.lib.nosql import get_db


class DataStream(object):
    """
    Datastream stored in collection named ds_<name>.
    Fields:
    _id: Object id
    changeid: Change ID
    data: stream data (serialized JSON)
    hash: Object hash
    """
    name = None

    F_ID = "_id"
    F_CHANGEID = "change_id"
    F_HASH = "hash"
    F_DATA = "data"
    F_META = "meta"
    HASH_LEN = 16

    DEFAULT_LIMIT = 1000
    rx_ts = re.compile(r"^\d{4}-\d{2}-\d{2}")

    @classmethod
    def get_collection_name(cls):
        return "ds_%s" % cls.name

    @classmethod
    def get_collection(cls):
        """
        Get pymongo Collection object
        :return:
        """
        coll = getattr(cls, "_collection", None)
        if not coll:
            coll = get_db()[cls.get_collection_name()]
            cls._collection = coll
        return coll

    @classmethod
    def ensure_collection(cls):
        """
        Ensure collection is created and properly indexed
        :return:
        """
        coll = cls.get_collection()
        coll.create_index(cls.F_CHANGEID, unique=True)

    @classmethod
    def get_object(cls, id):
        """
        Generate datastream object for given id.
        Raise KeyError if object is not found
        Must be overriden
        :param id: Object id
        :return: dict containing object data
        """
        raise NotImplementedError()

    @classmethod
    def get_meta(cls, data):
        """
        Extract additional metadata from .get_object() result for additional indexing
        :param data: .get_object() result
        :return: dict or None
        """
        return None

    @classmethod
    def get_deleted_object(cls, id):
        """
        Generate item for deleted object
        :param id:
        :return:
        """
        return {
            "id": id,
            "$deleted": True
        }

    @staticmethod
    def get_hash(data):
        return hashlib.sha256(ujson.dumps(data)).hexdigest()[:DataStream.HASH_LEN]

    @classmethod
    def update_object(cls, id, delete=False):
        """
        Generate and update object in stream
        :param id: Object id
        :param delete: Object must be marked as deleted
        :return: True if obbject has been updated
        """
        metrics["ds_%s_updated" % cls.name] += 1
        coll = cls.get_collection()
        # Build object for stream
        meta = None
        if delete:
            data = cls.get_deleted_object(id)
        else:
            try:
                data = cls.get_object(id)
                meta = cls.get_meta(data)
            except KeyError:
                data = cls.get_deleted_object(id)
        # Calculate hash
        hash = cls.get_hash(data)
        # Get existing object
        doc = coll.find_one({cls.F_ID: id}, {cls.F_ID: 0, cls.F_HASH: 1})
        if doc and doc.get(cls.F_HASH) == hash:
            return False  # Not changed
        metrics["ds_%s_changed" % cls.name] += 1
        changeid = bson.ObjectId()
        data["change_id"] = str(changeid)
        op = {
            "$set": {
                cls.F_CHANGEID: changeid,
                cls.F_HASH: hash,
                cls.F_DATA: ujson.dumps(data)
            }
        }
        if meta:
            op["$set"][cls.F_META] = meta
        elif "$deleted" not in data:
            op["$unset"] = {
                cls.F_META: ""
            }
        coll.update_one({
            cls.F_ID: id
        }, op, upsert=True)
        return True

    @classmethod
    def delete_object(cls, id):
        """
        Mark object as deleted
        :param id:
        :return:
        """
        cls.update_object(id, delete=True)

    @classmethod
    def get_total(cls):
        """
        Return total amount of items in datastream
        :return:
        """
        return cls.get_collection().count()

    @classmethod
    def clean_change_id(cls, change_id):
        """
        Convert change_id to ObjectId. Following formats are possible:
        * ObjectId
        * string containing ObjectId
        * ISO 8601 timestamp either in form
          * YYYY-DD-MM
          * YYYY-DD-MMThh:mm:ss
        :param change_id: Cleaned change_id
        :return:
        """
        # ObjectId
        if isinstance(change_id, bson.ObjectId):
            return change_id
        # String with timestamp or ObjectId
        if not isinstance(change_id, six.string_types):
            raise ValueError("Invalid change_id")
        if cls.rx_ts.search(change_id):
            # Timestamp
            try:
                ts = dateutil.parser.parse(change_id)
                return bson.ObjectId.from_datetime(ts)
            except ValueError as e:
                raise ValueError(str(e))
        # ObjectId
        try:
            return bson.ObjectId(change_id)
        except (bson.errors.InvalidId, TypeError) as e:
            raise ValueError(str(e))

    @classmethod
    def iter_data(cls, change_id=None, limit=None, filters=None):
        """
        Iterate over data items beginning from change id
        :param change_id: Staring change id
        :param limit: Records limit
        :param filters: List of strings with filter expression
        :return: (id, change_id, data)
        """
        q = {}
        if filters:
            q.update(cls.compile_filters(filters))
        if change_id:
            q[cls.F_CHANGEID] = {
                "$gt": cls.clean_change_id(change_id)
            }
        coll = cls.get_collection()
        for doc in coll.find(q, {
            cls.F_ID: 1,
            cls.F_CHANGEID: 1,
            cls.F_DATA: 1
        }).sort([
            (cls.F_CHANGEID, pymongo.ASCENDING)
        ]).limit(
            limit=limit or cls.DEFAULT_LIMIT
        ):
            yield doc[cls.F_ID], doc[cls.F_CHANGEID], doc[cls.F_DATA]

    @classmethod
    def clean_id(cls, id):
        """
        Convert arbitrary string to id data type
        Raise ValueError if invalid type given
        :param id:
        :return:
        """
        return id

    @classmethod
    def clean_id_int(cls, id):
        """
        Convert arbitrary string id to int
        :param id:
        :return:
        """
        return int(id)

    @classmethod
    def wait(cls):
        """
        Block until datastream receives changes
        :return:
        """
        coll = cls.get_collection()
        with coll.watch() as stream:
            next(stream)
            return

    @classmethod
    def _parse_filter(cls, expr):
        """
        Convert single filter expression to a S-expression
        :param expr: filter expression in form name(arg1, .., argN)
        :return: (name, arg1, argN)
        """
        if not isinstance(expr, six.string_types):
            raise ValueError("Expression must be string")
        i1 = expr.find("(")
        if i1 < 0:
            raise ValueError("Missed opening bracket")
        if not expr.endswith(")"):
            raise ValueError("Missed closing bracket")
        return [expr[:i1]] + [x.strip() for x in expr[i1 + 1:-1].split(",")]

    @classmethod
    def compile_filters(cls, exprs):
        """
        Compile list of filter expressions to MongoDB query
        :param exprs: List of strings with expressions
        :return: dict with query
        """
        if not isinstance(exprs, list):
            raise ValueError("expressions must be list of string")
        q = {}
        for fx in exprs:
            pv = cls._parse_filter(fx)
            h = getattr(cls, "filter_%s" % pv[0], None)
            if not h:
                raise ValueError("Invalid filter %s" % pv[0])
            q.update(h(*pv[1:]))
        return q

    @classmethod
    def filter_id(cls, id1, *args):
        """
        Filter by id. Usage:

        id(id1, .., idN)
        :param id1:
        :param args:
        :return:
        """
        ids = [cls.clean_id(id1)] + [cls.clean_id(x) for x in args]
        if len(ids) == 1:
            return {
                cls.F_ID: ids[0]
            }
        else:
            return {
                cls.F_ID: {
                    "$in": ids
                }
            }

    @classmethod
    def filter_shard(cls, instance, n_instances):
        """
        Sharding by id
        :param instance:
        :param n_instances:
        :return:
        """
        return {
            "_id": {
                "$mod": [int(n_instances), int(instance)]
            }
        }
