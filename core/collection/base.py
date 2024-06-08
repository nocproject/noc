# ----------------------------------------------------------------------
# Collection utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import zlib
import csv
import shutil
import hashlib
import uuid
from collections import namedtuple
import sys
import threading
import operator
from base64 import b85decode
from typing import Tuple, Dict

# Third-party modules
import orjson
import bson
from mongoengine.fields import (
    ListField,
    EmbeddedDocumentField,
    BinaryField,
    EmbeddedDocumentListField,
)
from mongoengine.errors import NotUniqueError
from mongoengine.document import Document
from pymongo import UpdateOne
import cachetools

# NOC modules
from noc.core.model.base import NOCModelBase
from noc.core.fileutils import safe_rewrite
from noc.config import config
from noc.core.mongo.connection import get_db
from noc.core.comp import smart_bytes
from noc.models import is_document
from django.db.utils import IntegrityError

state_lock = threading.Lock()


class Collection(object):
    PREFIX = "collections"
    CUSTOM_PREFIX = config.get_customized_paths(PREFIX, prefer_custom=True)
    STATE_COLLECTION = "noc.collectionstates"
    DEFAULT_API_VERSION = 1

    _MODELS = {}

    Item = namedtuple("Item", ["uuid", "path", "hash", "data"])
    _state_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __init__(self, name, stdout=None):
        self.name = name
        self._model = None
        self.ref_cache: Dict[Tuple[Document, str, str], Document] = {}
        self._name_field = None
        self.stdout = stdout or sys.stdout
        self.partial_errors = {}

    def get_path(self):
        paths = []
        for cp in config.get_customized_paths(self.PREFIX, prefer_custom=True):
            path = os.path.join(cp, self.name)
            if os.path.exists(path):
                paths += [path]
        return paths

    @classmethod
    def iter_collections(cls):
        from noc.models import COLLECTIONS, get_model

        for c in COLLECTIONS:
            cm = get_model(c)
            if is_document(cm):
                cn = cm._meta["json_collection"]
            else:
                cn = cm._json_collection["json_collection"]
            cls._MODELS[cn] = cm
            yield Collection(cn)

    @property
    def model(self):
        if not self._model:
            if not self._MODELS:
                list(self.iter_collections())
            self._model = self._MODELS[self.name]
        return self._model

    @property
    def name_field(self):
        if not self._name_field:
            if hasattr(self.model, "name"):
                self._name_field = "name"
                return "name"
            elif hasattr(self.model, "json_name"):
                self._name_field = "json_name"
                return "json_name"
            else:
                for spec in self.model._meta["index_specs"]:
                    if spec.get("unique") and len(spec["fields"]) == 1:
                        nf = spec["fields"][0][0]
                        self._name_field = nf
                        return nf
                raise ValueError("Cannot find unique index")
        else:
            return self._name_field

    def get_state_collection(self):
        """
        Return mongo collection for state
        :return:
        """
        return get_db()[self.STATE_COLLECTION]

    def get_state(self):
        """
        Returns collection state as a dict of UUID -> hash
        :return:
        """
        coll = self.get_state_collection()
        # Get state from database
        cs = coll.find_one({"_id": self.name})
        if cs:
            return orjson.loads(zlib.decompress(smart_bytes(cs["state"])))
        # Fallback to legacy local
        lpath = self.get_legacy_state_path()
        state = {}
        if os.path.exists(lpath):
            with open(lpath) as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for name, r_uuid, path, r_hash in reader:
                    state[r_uuid] = r_hash
        return state

    def save_state(self, state):
        """
        Save collection state
        :param state:
        :return:
        """
        coll = self.get_state_collection()
        coll.update_one(
            {"_id": self.name},
            {"$set": {"state": bson.Binary(zlib.compress(orjson.dumps(state)))}},
            upsert=True,
        )
        # Remove legacy state
        lpath = self.get_legacy_state_path()
        if os.path.isfile(lpath):
            shutil.move(lpath, lpath + ".bak")

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_state_cache"), lock=lambda _: state_lock)
    def get_builtins(cls, name):
        """
        Returns set of UUIDs for collection
        :param name:
        :return:
        """
        return set(Collection(name).get_state())

    def get_legacy_state_path(self):
        """
        Return legacy CSV state file path
        :return:
        """
        parts = self.name.split(".")
        return os.path.join("local", "collections", parts[0], "%s.csv" % parts[1])

    def get_changed_status(self):
        """
        Return initially changed status
        :return:
        """
        return os.path.isfile(self.get_legacy_state_path())

    def get_items(self):
        """
        Returns dict of UUID -> Collection.Item
        containing new state
        :return:
        """

        def item_hash_default(x):
            return hashlib.sha256(smart_bytes(x)).hexdigest()

        def item_hash_tagged(x):
            return "%s:%s" % (api_version, item_hash_default(x))

        # Get current API version and select proper hashing function
        # And build proper hashing function
        if is_document(self.model):
            api_version = self.model._meta.get("json_api_version", self.DEFAULT_API_VERSION)
        else:
            api_version = self.DEFAULT_API_VERSION
        if api_version == self.DEFAULT_API_VERSION:
            item_hash = item_hash_default
        else:
            item_hash = item_hash_tagged
        #
        items = {}
        for p in self.get_path():
            for root, dirs, files in os.walk(p):
                for cf in files:
                    if not cf.endswith(".json"):
                        continue
                    fp = os.path.join(root, cf)
                    with open(fp) as f:
                        data = f.read()
                    try:
                        jdata = orjson.loads(data)
                    except ValueError as e:
                        raise ValueError("Error load %s: %s" % (fp, e))
                    if "uuid" not in jdata:
                        raise ValueError("Invalid JSON %s: No UUID" % fp)
                    items[jdata["uuid"]] = self.Item(
                        uuid=jdata["uuid"], path=fp, hash=item_hash(data), data=jdata
                    )
        return items

    def get_fields(self, model: None):
        model = model or self.model
        if not isinstance(model, NOCModelBase):
            # Check Django Model
            return model._fields
        ls_field = model._meta.local_fields
        dc_field = {field.name: field.__class__ for field in ls_field}
        return dc_field

    def dereference(self, d, model=None):
        r = {}
        for k in d:
            v = d[k]
            if k.startswith("$"):
                continue  # Ignore $name
            if k == "uuid":
                r["uuid"] = uuid.UUID(v)
                continue
            # Dereference ref__name lookups
            if "__" in k:
                # Lookup
                k, f = k.split("__")
                if k not in self.get_fields(model):
                    raise ValueError("Invalid lookup field: %s" % k)
                ref = self.get_fields(model)[k].document_type
                v = self.lookup(ref, f, v)
            # Get field
            try:
                field = self.get_fields(model)[k]
            except KeyError:
                continue  # Ignore unknown fields
            # Dereference ListFields
            if (
                isinstance(field, ListField) and isinstance(field.field, EmbeddedDocumentField)
            ) or isinstance(field, EmbeddedDocumentListField):
                edoc = field.field.document_type
                try:
                    v = [edoc(**self.dereference(x, model=edoc)) for x in d[k]]
                except ValueError as e:
                    v = []
                    self.partial_errors[d["uuid"]] = str(e)
            elif isinstance(field, EmbeddedDocumentField):
                try:
                    v = field.document_type(**self.dereference(v, model=field.document_type))
                except ValueError as e:
                    v = None
                    self.partial_errors[d["uuid"]] = str(e)
            # Dereference binary field
            if isinstance(field, BinaryField):
                v = b85decode(v)
            r[str(k)] = v
        return r

    def lookup(self, ref: Document, field: str, key: str) -> Document:
        field = str(field)
        v = self.ref_cache.get((ref, field, key))
        if v:
            return v
        v = ref.objects.filter(**{field: key}).first()
        if v:
            self.ref_cache[ref, field, key] = v
            return v
        coll = ref._meta["collection"]
        raise ValueError(f"lookup for {coll}.{field} == '{key}' has been failed")

    def update_item(self, data):
        def set_attrs(obj, values):
            for vk in values:
                if hasattr(obj, vk):
                    setattr(obj, vk, values[vk])

        if data["uuid"] in self.partial_errors:
            del self.partial_errors[data["uuid"]]
        try:
            d = self.dereference(data)
        except ValueError as e:
            self.partial_errors[data["uuid"]] = str(e)
            return False  # Partials
        o = self.model.objects.filter(uuid=data["uuid"]).first()
        if o:
            self.stdout.write(
                "[%s|%s] Updating %s\n" % (self.name, data["uuid"], getattr(o, self.name_field))
            )
            set_attrs(o, d)
            o.save()
            return True
        else:
            self.stdout.write(
                "[%s|%s] Creating %s\n" % (self.name, data["uuid"], data.get(self.name_field))
            )
            o = self.model()
            set_attrs(o, d)
            try:
                o.save()
                return True
            except (NotUniqueError, IntegrityError):
                if is_document(self.model):
                    union_meta = self.model._meta
                else:
                    union_meta = self.model._json_collection
                # Possible local alternative with different uuid
                if not union_meta.get("json_unique_fields"):
                    self.stdout.write("Not json_unique_fields on object\n")
                    raise
                # Try to find conflicting item
                for k in union_meta["json_unique_fields"]:
                    if not isinstance(k, tuple):
                        k = (k,)
                    qs = {}
                    for fk in k:
                        if isinstance(d[fk], list):
                            qs["%s__in" % fk] = d[fk]
                        else:
                            qs[fk] = d[fk]
                    o = self.model.objects.filter(**qs).first()
                    if o:
                        self.stdout.write(
                            "[%s|%s] Changing local uuid %s (%s)\n"
                            % (self.name, data["uuid"], o.uuid, getattr(o, self.name_field))
                        )
                        o.uuid = data["uuid"]
                        if is_document(self.model):
                            o.save(clean=bool(o.uuid))
                        else:
                            o.save()
                        # Try again
                        return self.update_item(data)
                    self.stdout.write("Not find object by query: %s\n" % qs)
                raise

    def delete_item(self, uuid):
        o = self.model.objects.filter(uuid=uuid).first()
        if not o:
            return
        self.stdout.write("[%s|%s] Deleting %s\n" % (self.name, uuid, getattr(o, self.name_field)))
        o.delete()

    def sync(self):
        # Read collection from JSON files
        cdata = self.get_items()
        if not cdata:
            self.stdout.write("[%s] Ignoring empty collection\n" % self.name)
            return
        self.stdout.write("[%s] Synchronizing\n" % self.name)
        # Get previous state
        cs = self.get_state()
        #
        current_uuids = set(cs)
        new_uuids = set(cdata)
        changed = self.get_changed_status()
        #
        if is_document(self.model):
            self.fix_uuids()
        for u in new_uuids - current_uuids:
            self.update_item(cdata[u].data)
            changed = True
        # Changed items
        for u in new_uuids & current_uuids:
            if cs[u] != cdata[u].hash:
                self.update_item(cdata[u].data)
                changed = True
        # Resolve partials
        while self.partial_errors:
            pl = len(self.partial_errors)
            for u in list(self.partial_errors):  # may change size
                self.update_item(cdata[u].data)
            if len(self.partial_errors) == pl:
                # Cannot resolve partials
                for u in self.partial_errors:
                    self.stdout.write(
                        "[%s|%s] Error: %s\n" % (self.name, u, self.partial_errors[u])
                    )
                raise ValueError(
                    "[%s] Cannot resolve references for %s"
                    % (self.name, ", ".join(self.partial_errors))
                )
        # Deleted items
        for u in current_uuids - new_uuids:
            self.delete_item(u)
            changed = True
        # Save state
        if changed:
            state = {u: cdata[u].hash for u in sorted(cdata)}
            self.save_state(state)

    def fix_uuids(self):
        """
        Convert string UUIDs to binary
        :param name:
        :param model:
        :return:
        """
        bulk = []
        for d in self.model._get_collection().find(
            {"uuid": {"$type": "string"}}, {"_id": 1, "uuid": 1}
        ):
            bulk += [UpdateOne({"_id": d["_id"]}, {"$set": {"uuid": uuid.UUID(d["uuid"])}})]
        if bulk:
            self.stdout.write("[%s] Fixing %d UUID\n" % (self.name, len(bulk)))
            self.model._get_collection().bulk_write(bulk)

    @classmethod
    def install(cls, data):
        """
        Write data to the proper path
        :param data:
        :return:
        """
        c = Collection(data["$collection"])
        data = c.dereference(data)
        o = c.model(**data)
        # Format JSON
        json_data = o.to_json()
        # Write
        path = os.path.join(cls.PREFIX, c.name, o.get_json_path())
        if "uuid" not in data:
            raise ValueError("Invalid JSON: No UUID")
        c.stdout.write("[%s|%s] Installing %s\n" % (c.name, data["uuid"], path))
        safe_rewrite(path, json_data, mode=0o644)
