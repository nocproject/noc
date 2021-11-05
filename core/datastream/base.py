# ----------------------------------------------------------------------
# DataStream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import hashlib
import datetime
import re
import logging
from collections import defaultdict

# Third-party modules
import orjson
import bson
import bson.errors
import pymongo
import dateutil.parser
from typing import Optional, Dict, Any, List, Union, Iterable, Tuple, Callable

# NOC modules
from noc.core.perf import metrics
from noc.core.mongo.connection import get_db
from noc.core.comp import smart_text, smart_bytes
from noc.models import get_model
from noc.core.hash import hash_int
from noc.core.mx import send_message, MX_CHANGE_ID

logger = logging.getLogger(__name__)


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
    model = None  # PydanticModel for Response

    # Generate separate message
    enable_message = False

    F_ID = "_id"
    F_CHANGEID = "change_id"
    F_HASH = "hash"
    F_DATA = "data"
    F_META = "meta"
    HASH_LEN = 16

    DEFAULT_LIMIT = 1000
    rx_ts = re.compile(r"^\d{4}-\d{2}-\d{2}")

    BULK_SIZE = 500

    _collections: Dict[str, pymongo.collection.Collection] = {}
    _collections_async: Dict[str, pymongo.collection.Collection] = {}

    @classmethod
    def get_collection_name(cls, format: Optional[str] = None) -> str:
        if format:
            return "ds_%s_%s" % (cls.name, format)
        return "ds_%s" % cls.name

    @classmethod
    def get_collection(cls, fmt: Optional[str] = None) -> pymongo.collection.Collection:
        """
        Get pymongo Collection object
        :return:
        """
        c_name = cls.get_collection_name(fmt)
        coll = cls._collections.get(c_name)
        if not coll:
            coll = get_db()[c_name]
            cls._collections[c_name] = coll
        return coll

    @classmethod
    def get_collection_async(cls, fmt: Optional[str] = None) -> pymongo.collection.Collection:
        """
        Get pymongo Collection object
        :return:
        """
        c_name = cls.get_collection_name(fmt)
        if c_name not in cls._collections_async:
            from noc.core.mongo.connection_async import connect_async, get_db

            connect_async()
            coll = get_db()[c_name]
            cls._collections_async[c_name] = coll
        return cls._collections_async[c_name]

    @classmethod
    def ensure_collection(cls):
        """
        Ensure collection is created and properly indexed
        :return:
        """
        coll = cls.get_collection()
        coll.create_index(cls.F_CHANGEID, unique=True)
        meta = cls.get_meta({})
        if meta:
            for m in meta:
                coll.create_index("%s.%s" % (cls.F_META, m))

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
    def get_meta(cls, data: Dict[str, Any]) -> Optional[Dict]:
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
        return {"id": str(id), "$deleted": True}

    @staticmethod
    def get_hash(data) -> str:
        return hashlib.sha256(orjson.dumps(data)).hexdigest()[: DataStream.HASH_LEN]

    @classmethod
    def bulk_update(cls, objects: List[Union[id, str, bson.ObjectId]]) -> None:
        coll = cls.get_collection()
        # Get possible formats
        fmt_coll: Dict[str, pymongo.collection.Collection] = {}
        fmt_handler: Dict[str, Callable] = {}
        for fmt, handler in cls.iter_formats():
            fmt_coll[fmt] = cls.get_collection(fmt)
            fmt_handler[fmt] = handler
        # Process objects
        while objects:
            chunk, objects = objects[: cls.BULK_SIZE], objects[cls.BULK_SIZE :]
            current_state = {
                doc[cls.F_ID]: doc
                for doc in coll.find({cls.F_ID: {"$in": chunk}}, {cls.F_ID: 1, cls.F_HASH: 1})
            }
            bulk = []
            fmt_data = defaultdict(list)
            fmt_bulk = {}
            # Apply default format
            for obj_id in chunk:
                data, meta = cls._get_current_data(obj_id)
                cls._update_object(data=data, meta=meta, state=current_state, bulk=bulk)
                # Process formats
                for fmt in fmt_handler:
                    fmt_data[fmt] += list(fmt_handler[fmt](data))
            # Apply formats
            for fmt in fmt_data:
                fmt_ids = [data["id"] for data in fmt_data[fmt]]
                current_state = {
                    doc[cls.F_ID]: doc
                    for doc in fmt_coll[fmt].find(
                        {cls.F_ID: {"$in": fmt_ids}}, {cls.F_ID: 1, cls.F_HASH: 1}
                    )
                }
                fmt_bulk[fmt] = []
                for data in fmt_data[fmt]:
                    cls._update_object(data=data, fmt=fmt, state=current_state, bulk=fmt_bulk[fmt])
            # Save pending operations
            if bulk:
                logger.info("[%s] Sending %d bulk operations", cls.name, len(bulk))
                coll.bulk_write(bulk, ordered=True)
            for fmt in fmt_bulk:
                bulk = fmt_bulk[fmt]
                if bulk:
                    logger.info("[%s|%s] Sending %d bulk operations", cls.name, fmt, len(bulk))
                    fmt_coll[fmt].bulk_write(bulk, ordered=True)

    @classmethod
    def _update_object(cls, data, meta=None, fmt=None, state=None, bulk=None) -> bool:
        def is_changed(d, h):
            return not d or d.get(cls.F_HASH) != h

        obj_id = cls.clean_id(data["id"])
        if meta is None and "$meta" in data:
            meta = data.pop("$meta")
        m_name = "%s_%s" % (cls.name, fmt) if fmt else cls.name
        l_name = "%s|%s|%s" % (cls.name, obj_id, fmt) if fmt else "%s|%s" % (cls.name, obj_id)
        metrics["ds_%s_updated" % m_name] += 1
        # Calculate hash
        hash = cls.get_hash(data)
        # Get existing object state
        if state:
            doc = state.get(obj_id)
        else:
            doc = cls.get_collection(fmt).find_one({cls.F_ID: obj_id}, {cls.F_ID: 0, cls.F_HASH: 1})
        if not is_changed(doc, hash):
            logger.info("[%s] Object hasn't been changed", l_name)
            return False  # Not changed
        if not fmt and cls.on_change(data):
            hash = cls.get_hash(data)
            if not is_changed(doc, hash):
                logger.info("[%s] Object hasn't been changed", l_name)
                return False  # Not changed after altering
        metrics["ds_%s_changed" % m_name] += 1
        change_id = bson.ObjectId()
        data["change_id"] = str(change_id)
        op = {
            "$set": {
                cls.F_CHANGEID: change_id,
                cls.F_HASH: hash,
                cls.F_DATA: smart_text(orjson.dumps(data)),
            }
        }
        if meta:
            op["$set"][cls.F_META] = meta
        elif "$deleted" not in data:
            op["$unset"] = {cls.F_META: ""}
        if bulk is None:
            cls.get_collection(fmt).update_one({cls.F_ID: obj_id}, op, upsert=True)
        else:
            bulk += [pymongo.UpdateOne({cls.F_ID: obj_id}, op, upsert=True)]
        logger.info("[%s] Object has been changed", l_name)
        if cls.enable_message:
            # Build MX message
            logger.info("[%s] Sending message", l_name)
            cls.send_message(data, change_id)
        return True

    @classmethod
    def _get_current_data(
        cls, obj_id, delete=False
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        if delete:
            return cls.get_deleted_object(obj_id), None
        try:
            data = cls.get_object(obj_id)
            meta = cls.get_meta(data)
            return data, meta
        except KeyError:
            return cls.get_deleted_object(obj_id), None

    @classmethod
    def update_object(cls, id, delete=False) -> bool:
        """
        Generate and update object in stream
        :param id: Object id
        :param delete: Object must be marked as deleted
        :return: True if object has been updated
        """
        data, meta = cls._get_current_data(id, delete=delete)
        r = cls._update_object(data=data, meta=meta)
        for fmt, handler in cls.iter_formats():
            for f_data in handler(data):
                r |= cls._update_object(data=f_data, fmt=fmt)
        return r

    @classmethod
    def delete_object(cls, id):
        """
        Mark object as deleted
        :param id:
        :return:
        """
        cls.update_object(id, delete=True)

    @classmethod
    def iter_formats(
        cls,
    ) -> Iterable[Tuple[str, Callable[[Dict[str, Any]], Iterable[Dict[str, Any]]]]]:
        # Do not load in datastream service
        DataStreamConfig = getattr(cls, "_DataStreamConfig", None)
        if not DataStreamConfig:
            cls._DataStreamConfig = get_model("main.DataStreamConfig")
            DataStreamConfig = cls._DataStreamConfig

        cfg = DataStreamConfig.get_by_name(cls.name)
        if cfg:
            yield from cfg.iter_formats()

    @classmethod
    def get_total(cls, fmt=None):
        """
        Return total amount of items in datastream
        :return:
        """
        return cls.get_collection(fmt).estimated_document_count()

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
        if not isinstance(change_id, str):
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
    async def iter_data_async(cls, change_id, limit, filters, fmt):
        q = {}
        if filters:
            q.update(cls.compile_filters(filters))
        if change_id:
            q[cls.F_CHANGEID] = {"$gt": cls.clean_change_id(change_id)}
        coll = cls.get_collection_async(fmt)
        async for doc in (
            coll.find(q, {cls.F_ID: 1, cls.F_CHANGEID: 1, cls.F_DATA: 1})
            .sort([(cls.F_CHANGEID, pymongo.ASCENDING)])
            .limit(limit=limit or cls.DEFAULT_LIMIT)
        ):
            yield doc[cls.F_ID], doc[cls.F_CHANGEID], doc[cls.F_DATA]

    @classmethod
    def iter_data(cls, change_id=None, limit=None, filters=None, fmt=None):
        """
        Iterate over data items beginning from change id

        Raises ValueError if filters has incorrect input parameters
        :param change_id: Staring change id
        :param limit: Records limit
        :param filters: List of strings with filter expression
        :param fmt: Format
        :return: (id, change_id, data)
        """
        q = {}
        if filters:
            q.update(cls.compile_filters(filters))
        if change_id:
            q[cls.F_CHANGEID] = {"$gt": cls.clean_change_id(change_id)}
        coll = cls.get_collection(fmt)
        for doc in (
            coll.find(q, {cls.F_ID: 1, cls.F_CHANGEID: 1, cls.F_DATA: 1})
            .sort([(cls.F_CHANGEID, pymongo.ASCENDING)])
            .limit(limit=limit or cls.DEFAULT_LIMIT)
        ):
            yield doc[cls.F_ID], doc[cls.F_CHANGEID], doc[cls.F_DATA]

    @classmethod
    def on_change(cls, data):
        """
        Called when datastream changed. May alter data
        :param data:
        :return: True, if data is altered and hash must be recalculated
        """
        return False

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
    def clean_id_bson(cls, id):
        """
        Convert arbitrary string id to bson int
        :param id:
        :return:
        """
        return bson.ObjectId(id)

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

    @staticmethod
    def qs(s):
        """
        Encode string to utf-8
        :param s:
        :return:
        """
        if not s:
            return ""
        if isinstance(s, datetime.datetime):
            return s.isoformat()
        return smart_text(s)

    @classmethod
    def _parse_filter(cls, expr):
        """
        Convert single filter expression to a S-expression
        :param expr: filter expression in form name(arg1, .., argN)
        :return: (name, arg1, argN)
        """
        if not isinstance(expr, str):
            raise ValueError("Expression must be string")
        i1 = expr.find("(")
        if i1 < 0:
            raise ValueError("Missed opening bracket")
        if not expr.endswith(")"):
            raise ValueError("Missed closing bracket")
        return [expr[:i1]] + [x.strip() for x in expr[i1 + 1 : -1].split(",")]

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
            return {cls.F_ID: ids[0]}
        return {cls.F_ID: {"$in": ids}}

    @classmethod
    def filter_shard(cls, instance, n_instances):
        """
        Sharding by id
        :param instance:
        :param n_instances:
        :return:
        """
        # Raise ValueError if not integer
        instance = int(instance)
        n_instances = int(n_instances)
        #
        if n_instances < 1:
            raise ValueError("Invalid number of instances")
        if instance < 0:
            raise ValueError("Invalid instance")
        if instance >= n_instances:
            raise ValueError("Invalid instance")
        return {"_id": {"$mod": [n_instances, instance]}}

    @classmethod
    def get_format_role(cls, fmt: str) -> Optional[str]:
        """
        Returns format role, if any
        :param fmt:
        :return:
        """
        doc = get_db()["datastreamconfigs"].find_one({"name": cls.name})
        if not doc:
            return None
        for f in doc.get("formats", []):
            if f.get("name") == fmt:
                return f.get("role") or None
        return None

    @classmethod
    def get_msg_headers(cls, data: Dict[str, Any]) -> Optional[Dict[str, bytes]]:
        return None

    @classmethod
    def send_message(cls, data: Dict[str, Any], change_id: bson.ObjectId) -> None:
        """
        Send MX message

        :param data:
        :param change_id:
        :return:
        """
        data["$changeid"] = str(change_id)
        # Build headers
        headers = {
            MX_CHANGE_ID: smart_bytes(change_id),
        }
        additional_headers = cls.get_msg_headers(data)
        if additional_headers:
            headers.update(additional_headers)
        # Schedule to send
        send_message(
            data,
            message_type=cls.name,
            headers=headers,
            sharding_key=hash_int(data["id"]) & 0xFFFFFFFF,
        )
        # Cleanup
        del data["$changeid"]
