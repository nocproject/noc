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
## Third-party modules
from mongoengine.fields import ListField, EmbeddedDocumentField
## NOC modules
from noc.lib.fileutils import safe_rewrite
from noc.lib.serialize import json_decode
from noc.main.models.collectioncache import CollectionCache


CollectionItem = namedtuple("CollectionItem", [
    "name", "uuid", "path", "hash"])


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
        partial = set()
        # Delete revoked items
        for i in collection.get_revoked_items():
            if i in self.items:
                self.delete_item(i)
        # Check for new items
        for i in sr - sl:
            try:
                self.update_item(collection.items[i])
            except ValueError:
                partial.add(i)
        # Update changed items
        for i in sr & sl:
            if self.items[i].hash != collection.items[i].hash:
                try:
                    self.update_item(collection.items[i])
                except ValueError:
                    partial.add(i)
        # Update partial items
        for i in partial:
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

    def create_item(self, mi):
        self.log(u"    ... creating %s" % mi.name)
        data = self.load_item(mi)
        doc = self.doc(**self.dereference(self.doc, data))
        doc.save()
        self.items[mi.uuid] = mi
        self.changed = True

    def update_item(self, mi):
        o = self.doc.objects.filter(uuid=mi.uuid).first()
        if not o:
            self.create_item(mi)
            return
        self.log(u"    ... updating %s" % unicode(o))
        data = self.load_item(mi)
        d = self.dereference(self.doc, data)
        for k in d:
            setattr(o, k, d[k])
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
                self.die("lookup for %s.%s == '%s' has been failed" % (
                    ref._meta["collection"], field, key))
            self.ref_cache[ref][field][key] = v
            return v

    def dereference(self, doc, d):
        r = {}
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
                self.die("Unknown field: '%s'" % k)
            # Dereference ListFields
            if (type(field) == ListField and
                    isinstance(field.field, EmbeddedDocumentField)):
                edoc = field.field.document_type
                v = [edoc(**self.dereference(edoc, x)) for x in d[k]]
            r[str(k)] = v
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
                name=o.name,
                uuid=o.uuid,
                path=o.get_json_path(),
                hash=self.get_hash(data)
            )
            self.items[mi.uuid] = mi
            self.log("    ... importing %s" % o.name)
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
            o = self.doc.objects.filter(uuid=d["uuid"]).first()
            if o:
                return
            for un in unique:
                o = self.doc.objects.filter(**{un: d[un]}).first()
                if o:
                    self.log("    ... upgrading %s" % unicode(o))
                    o.uuid = d["uuid"]
                    o.save()

        self.log("Upgrading %s.%s" % (self.module, self.name))
        # Define set of unique fields
        unique = set()
        for index in self.doc._meta["unique_indexes"]:
            for f, flag in index:
                unique.add(f)
        for u in collection.items:
            try:
                upgrade_item(u)
            except ValueError:
                pass

    def install_item(self, data):
        o = self.doc(**self.dereference(self.doc, data))
        self.log("    ... installing %s" % unicode(o))
        if not o.uuid:
            o.uuid = uuid.uuid4()
        dd = o.to_json()
        mi = CollectionItem(
            name=o.name,
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
