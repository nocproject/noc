# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collection synchronization
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import csv
from collections import namedtuple
from cStringIO import StringIO
import hashlib
import uuid
from operator import attrgetter
import logging
## Third-party modules
from mongoengine.fields import ListField, EmbeddedDocumentField
from mongoengine.queryset import Q
## NOC modules
from noc.lib.fileutils import safe_rewrite
from noc.lib.serialize import json_decode
from noc.main.models.collectioncache import CollectionCache

logger = logging.getLogger(__name__)


CollectionItem = namedtuple("CollectionItem", [
    "name", "uuid", "path", "hash"])


class DereferenceError(Exception):
    pass


class Collection(object):
    def __init__(self, name, doc, local=False):
        m, c = name.split(".", 1)
        self.module = m
        self.name = c
        self.local = local
        self.doc = doc
        self.items = {}  # uuid -> CollectionItem
        self.changed = False
        self.ref_cache = {}
        self.partial = set()
        if hasattr(self.doc, "name"):
            # Use .name field when present
            self.get_name = attrgetter("name")
        else:
            # Or first unique field otherwise
            uname = None
            for spec in self.doc._meta["index_specs"]:
                if spec["unique"] and len(spec["fields"]) == 1:
                    uname = spec["fields"][0][0]
            if not uname:
                logger.error("Cannot find unique index")
                raise ValueError("No unique index")
            self.get_name = attrgetter(uname)

    def log(self, msg):
        print msg

    def die(self, msg):
        raise ValueError(msg)

    def get_collection_path(self):
        if self.local:
            return os.path.join("local", "collections",
                                self.module, self.name + ".csv")
        else:
            return os.path.join(self.module, "collections",
                                self.name, "manifest.csv")

    def get_item_path(self, mi):
        return os.path.join(
            self.module, "collections", self.name, mi.path)

    def load(self):
        """
        Load collection from CSV file
        """
        path = self.get_collection_path()
        if not os.path.exists(path):
            return
        with open(path) as f:
            reader = csv.reader(f)
            header = reader.next()
            for name, uuid, path, hash in reader:
                mi = CollectionItem(
                    name=name, uuid=uuid, path=path, hash=hash)
                self.items[uuid] = mi

    def save(self):
        self.log("Updating manifest")
        rows = sorted(
            ([r.name, r.uuid, r.path, r.hash]
             for r in self.items.values()),
            key=lambda x: x[0]
        )
        rows = [["name", "uuid", "path", "hash"]] + rows
        out = StringIO()
        writer = csv.writer(out)
        writer.writerows(rows)
        safe_rewrite(self.get_collection_path(), out.getvalue(),
                     mode=0644)
        # Update collection cache
        self.log("Updating CollectionCache")
        CollectionCache.merge(
            "%s.%s" % (self.module, self.name), set(self.items)
        )

    def load_item(self, mi):
        p = self.get_item_path(mi)
        if not os.path.exists(p):
            self.die("File not found: %s" % p)
        with open(p) as f:
            fdata = f.read()
            try:
                data = json_decode(fdata)
            except ValueError, why:
                self.die("Failed to read JSON file '%s': %s" % (p, why))
        if not isinstance(data, dict):
            self.die("Invalid JSON file: %s" % p)
        if self.get_hash(fdata) != mi.hash:
            self.die("Checksum mismatch for file '%s'" % p)
        return data

    def get_hash(self, data):
        return hashlib.sha256(data).hexdigest()

    def check_item(self, mi):
        path = self.get_item_path(mi)
        if not os.path.exists(path):
            return ["File not found: %s" % path]
        with open(path) as f:
            hash = self.get_hash(f.read())
        if hash != mi.hash:
            return ["Checksum mismatch: %s" % path]
        return []

    def get_revoked_items(self):
        """
        Returns set of revoked items
        """
        return set(i for i in self.items if not self.items[i].name)

    def apply(self, collection):
        if not self.items:
            # Empty local file, needs to upgrade collection first
            self.upgrade_collection(collection)
        self.log("Syncing %s.%s" % (self.module, self.name))
        sl = set(self.items)
        sr = set(collection.items)
        # Delete revoked items
        for i in collection.get_revoked_items():
            if i in self.items:
                self.delete_item(i)
        # Check for new items
        for i in sr - sl:
            self.update_item(collection.items[i])
        # Update changed items
        for i in sr & sl:
            if self.items[i].hash != collection.items[i].hash:
                self.update_item(collection.items[i])
        # Update partial items
        for i in self.partial:
            self.update_item(collection.items[i])
        if self.changed:
            self.save()

    def delete_item(self, u):
        o = self.doc.get(uuid=u).first()
        if not o:
            return
        self.log(u"    ... deleting %s" % unicode(o))
        o.delete()
        del self.items[u]
        self.changed = True

    def get_by_uuid(self, u):
        """
        Returns object instance or None
        """
        return self.doc.objects.filter(
            Q(uuid=u) | Q(uuid=uuid.UUID(u))
        ).first()

    def update_item(self, mi):
        o = self.get_by_uuid(mi.uuid)
        if o:
            self.log(u"    ... updating %s" % unicode(o))
        else:
            self.log(u"    ... creating %s" % mi.name)
        data = self.load_item(mi)
        try:
            d = self.dereference(self.doc, data)
        except DereferenceError:
            self.log(u"    ... processing delayed due to possible circular reference")
            self.partial.add(mi.uuid)
            return
        if o:
            # Update fields
            for k in d:
                setattr(o, k, d[k])
        else:
            # Create item
            o = self.doc(**d)
        o.save()
        self.items[mi.uuid] = mi
        self.changed = True

    def lookup(self, ref, field, key):
        field = str(field)
        if ref not in self.ref_cache:
            self.ref_cache[ref] = {field: {}}
        if field not in self.ref_cache[ref]:
            self.ref_cache[ref][field] = {}
        if key in self.ref_cache[ref][field]:
            return self.ref_cache[ref][field][key]
        else:
            try:
                v = ref.objects.get(**{field: key})
            except ref.DoesNotExist:
                raise DereferenceError(
                    "lookup for %s.%s == '%s' has been failed" % (
                        ref._meta["collection"], field, key)
                )
            self.ref_cache[ref][field][key] = v
            return v

    def dereference(self, doc, d):
        r = {}
        partial = False
        for k in d:
            v = d[k]
            # Dereference ref__name lookups
            if "__" in k:
                # Lookup
                k, f = k.split("__")
                if k not in doc._fields:
                    self.die("Invalid lookup field: %s" % k)
                ref = doc._fields[k].document_type
                v = self.lookup(ref, f, v)
            # Get field
            try:
                field = doc._fields[k]
            except KeyError:
                continue  # Ignore unknown fields
            # Dereference ListFields
            if (type(field) == ListField and
                    isinstance(field.field, EmbeddedDocumentField)):
                edoc = field.field.document_type
                try:
                    v = [edoc(**self.dereference(edoc, x)) for x in d[k]]
                except DereferenceError, why:
                    # Deferred partial
                    v = []
                    partial = True
            r[str(k)] = v
        if partial:
            self.partial.add(d["uuid"])
        return r

    def import_files(self, paths):
        for p in paths:
            if not os.path.exists(p):
                raise ValueError("File does not exists: %s" % p)
            with open(p) as f:
                try:
                    data = json_decode(f.read())
                except ValueError, why:
                    self.die("Failed to read JSON file '%s': %s" % (p, why))
            if not isinstance(data, dict):
                self.die("Invalid JSON file: %s" % p)
            doc = self.doc(**self.dereference(self.doc, data))
            mi = CollectionItem(
                name=doc.name,
                uuid=doc.uuid,
                path=doc.get_json_path(),
                hash=self.get_hash(data)
            )
            self.items[mi.uuid] = mi
            self.log("    ... importing %s" % doc.name)
            safe_rewrite(os.path.join(
                self.module, "collections",
                self.name, doc.get_json_path()),
                data,
                mode=0644
            )
        if paths:
            self.save()

    def import_objects(self, objects):
        for o in objects:
            if not o.uuid:
                o.uuid = uuid.uuid4()
                o.save()
            data = o.to_json()
            mi = CollectionItem(
                name=self.get_name(o),
                uuid=o.uuid,
                path=o.get_json_path(),
                hash=self.get_hash(data)
            )
            self.items[mi.uuid] = mi
            self.log("    ... importing %s" % mi.name)
            safe_rewrite(os.path.join(
                self.module, "collections", self.name,
                o.get_json_path()),
                data,
                mode=0644
            )
        self.save()

    def upgrade_collection(self, collection):
        """
        First-time collection upgrade
        """
        def upgrade_item(u):
            d = self.load_item(collection.items[u])
            if d is None:
                p = self.get_item_path(collection.items[u])
                self.die("File not found: %s" % p)
            d = self.dereference(self.doc, d)
            o = self.get_by_uuid(d["uuid"])
            if o:
                return  # Already upgraded
            for un in unique:
                o = self.doc.objects.filter(**{un: d[un]}).first()
                if o:
                    self.log("    ... upgrading %s" % unicode(o))
                    o.uuid = d["uuid"]
                    o.save()
                    break

        self.log("Upgrading %s.%s" % (self.module, self.name))
        # Define set of unique fields
        unique = set()
        for spec in self.doc._meta["index_specs"]:
            for f, flag in spec["fields"]:
                if spec.get("unique") and len(spec["fields"]) == 2:
                    unique.add(f)
        for u in collection.items:
            try:
                upgrade_item(u)
            except DereferenceError:
                pass

    def install_item(self, data, load=False):
        o = self.doc(**self.dereference(self.doc, data))
        self.log("    ... installing %s" % unicode(o))
        if not o.uuid:
            o.uuid = str(uuid.uuid4())
            load = False  # Cannot load due to uuid collision
        dd = o.to_json()
        mi = CollectionItem(
            name=self.get_name(o),
            uuid=o.uuid,
            path=o.get_json_path(),
            hash=self.get_hash(dd)
        )
        self.items[mi.uuid] = mi
        safe_rewrite(os.path.join(
            self.module, "collections", self.name,
            o.get_json_path()),
            dd,
            mode=0644
        )
        if load:
            # Save to database
            self.update_item(mi)

    def get_status(self):
        # Reindex items
        items = {}  # Path -> CollectionItem
        for ci in self.items.itervalues():
            items[ci.path] = ci
        prefix = os.path.join(self.module, "collections", self.name)
        for root, dirnames, files in os.walk(prefix):
            r = os.path.sep.join(root.split(os.path.sep)[3:])
            for f in files:
                if f.endswith(".json"):
                    path = os.path.join(r, f)
                    if path in items:
                        rpath = os.path.join(root, f)
                        if os.path.exists(rpath):
                            with open(rpath) as f:
                                h = self.get_hash(f.read())
                            if h == items[path].hash:
                                continue  # Not changed
                            else:
                                yield "M", path  # Modified
                        else:
                            yield "!", path  # Removed
                    else:
                        yield "?", path
