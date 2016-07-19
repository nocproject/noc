# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collections manipulation
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from collections import namedtuple
import hashlib
import zlib
import csv
import shutil
import uuid
import argparse
## Third-party modules
import ujson
import bson
from mongoengine.fields import ListField, EmbeddedDocumentField
## NOC modules
from noc.core.management.base import BaseCommand
from noc.models import get_model, COLLECTIONS
from noc.lib.nosql import get_db
from noc.lib.fileutils import safe_rewrite


CollectionItem = namedtuple("CollectionItem", [
    "uuid", "path", "hash", "data"])
STATE_COLLECTION = "noc.collectionstates"


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            dest="cmd",
            help="sub-commands help"
        )
        # sync
        sync_parser = subparsers.add_parser(
            "sync",
            help="Synchronize collections"
        )
        # install
        install_parser = subparsers.add_parser(
            "install",
            help="Add collections to repository"
        )
        install_parser.add_argument(
            "-r", "--remove",
            dest="remove",
            action="store_true",
            help="Remove installed files"
        )
        install_parser.add_argument(
            "install_files",
            nargs=argparse.REMAINDER,
            help="List of files"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def iter_collections(self):
        for c in COLLECTIONS:
            cm = get_model(c)
            cn = cm._meta["json_collection"]
            yield cm, cn

    def get_collection_path(self, name):
        return os.path.join("collections", name)

    def get_collection(self, prefix):
        #
        items = {}
        paths = [prefix]
        # Check for custom path
        cprefix = os.path.join("custom", prefix)
        if os.path.isdir(cprefix):
            paths += [cprefix]

        for p in paths:
            for root, dirs, files in os.walk(p):
                for cf in files:
                    if not cf.endswith(".json"):
                        continue
                    fp = os.path.join(root, cf)
                    with open(fp) as f:
                        data = f.read()
                    jdata = ujson.loads(data)
                    csum = hashlib.sha256(data).hexdigest()
                    items[jdata["uuid"]] = CollectionItem(
                        uuid=jdata["uuid"],
                        path=fp,
                        hash=csum,
                        data=jdata
                    )
        return items

    def get_name_field(self, model):
        if not hasattr(model, "_name_field"):
            if hasattr(model, "name"):
                model._name_field = "name"
                return "name"
            else:
                for spec in model._meta["index_specs"]:
                    if spec["unique"] and len(spec["fields"]) == 1:
                        nf = spec["fields"][0][0]
                        model._name_field = nf
                        return nf
                raise ValueError("Cannot find unique index")
        else:
            return model._name_field

    def get_collection_state(self, name):
        """
        Returns collection current state as dict uuid -> hash
        :param name:
        :return:
        """
        # Get state from database
        cs = self.state_collection.find_one({"_id": name})
        if cs:
            return ujson.loads(
                zlib.decompress(str(cs["state"]))
            )
        # Fallback to legacy local
        lpath = self.get_legacy_state_path(name)
        state = {}
        if os.path.exists(lpath):
            with open(lpath) as f:
                reader = csv.reader(f)
                reader.next()  # Skip header
                for name, uuid, path, hash in reader:
                    state[uuid] = hash
        return state

    def get_legacy_state_path(self, name):
        """
        Return collection's legacy CSV path
        :param name:
        :return:
        """
        parts = name.split(".")
        return os.path.join("local", "collections",
                             parts[0], "%s.csv" % parts[1])

    def save_collection_state(self, name, state):
        """
        Save collection state
        :param name:
        :param state: dict of uuid -> hash
        :return:
        """
        self.state_collection.update({
            "_id": name,
        }, {
            "$set": {
                "state": bson.Binary(
                    zlib.compress(
                        ujson.dumps(state)
                    )
                )
            }
        }, upsert=True)
        # Remove legacy state
        lpath = self.get_legacy_state_path(name)
        if os.path.isfile(lpath):
            shutil.move(lpath, lpath + ".bak")

    def handle_sync(self):
        self.state_collection = get_db()[STATE_COLLECTION]
        self.ref_cache = {}
        for cm, cn in self.iter_collections():
            # Read collection from JSON files
            cdata = self.get_collection(
                self.get_collection_path(cn)
            )
            # Get previous state
            cs = self.get_collection_state(cn)
            #
            current_uuids = set(cs)
            new_uuids = set(cdata)
            changed = os.path.isfile(self.get_legacy_state_path(cn))
            #
            self.fix_uuids(cn, cm)
            partials = []
            # New items
            for u in new_uuids - current_uuids:
                if not self.update_item(cn, cm, cdata[u].data):
                    partials += [u]
                changed = True
            # Changed items
            for u in new_uuids & current_uuids:
                if cs[u] != cdata[u].hash:
                    if not self.update_item(cn, cm, cdata[u].data):
                        partials += [u]
                    changed = True
            # Resolve partials
            while partials:
                pl = len(partials)
                np = []
                for u in partials:
                    if not self.update_item(cn, cm, cdata[u].data):
                        np += u
                if len(np) == len(partials):
                    # Cannot resolve partials
                    self.die("[%s] Cannot resolve references for %s" % (
                        cn, ", ".join(partials)
                    ))
                partials = np
            # Deleted items
            for u in current_uuids - new_uuids:
                self.delete_item(cn, cm, u)
                changed = True
            # Save state
            if changed:
                state = dict((u, cdata[u].hash) for u in sorted(cdata))
                self.save_collection_state(cn, state)

    def fix_uuids(self, name, model):
        """
        Convert string UUIDs to binary
        :param name:
        :param model:
        :return:
        """
        n = 0
        bulk = model._get_collection().initialize_unordered_bulk_op()
        for d in model._get_collection().find(
            {
                "uuid": {"$type": "string"}
            },
            {
                "_id": 1,
                "uuid": 1
            }
        ):
            bulk.find({"_id": d["_id"]}).update({
                "$set": {
                    "uuid": uuid.UUID(d["uuid"])
                }
            })
            n += 1
        if n:
            self.stdout.write("[%s] Fixing %d UUID\n" % (
                name, n
            ))
            bulk.execute()

    def update_item(self, name, model, data):
        o = model.objects.filter(uuid=data["uuid"]).first()
        try:
            d = self.dereference(model, data)
        except ValueError:
            return False  # Partials
        if o:
            self.stdout.write(
                "[%s|%s] Updating %s\n" % (
                    name, data["uuid"],
                    getattr(o, self.get_name_field(model))
            ))
            for k in d:
                setattr(o, k, d[k])
        else:
            self.stdout.write(
                "[%s|%s] Creating %s\n" % (
                    name, data["uuid"],
                    data.get(self.get_name_field(model))
            ))
            o = model(**d)
        o.save()
        return True

    def delete_item(self, name, model, uuid):
        o = model.objects.filter(uuid=uuid).first()
        if not o:
            return
        self.stdout.write("[%s|%s] Deleting %s\n" % (
            name, uuid, getattr(o, self.get_name_field(model))
        ))
        o.delete()

    def dereference(self, model, d):
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
                if k not in model._fields:
                    self.die("Invalid lookup field: %s" % k)
                ref = model._fields[k].document_type
                v = self.lookup(ref, f, v)
            # Get field
            try:
                field = model._fields[k]
            except KeyError:
                continue  # Ignore unknown fields
            # Dereference ListFields
            if (type(field) == ListField and
                    isinstance(field.field, EmbeddedDocumentField)):
                edoc = field.field.document_type
                v = [edoc(**self.dereference(edoc, x)) for x in d[k]]
            r[str(k)] = v
        return r

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
                raise ValueError(
                    "lookup for %s.%s == '%s' has been failed" % (
                        ref._meta["collection"], field, key)
                )
            self.ref_cache[ref][field][key] = v
            return v

    def handle_install(self, install_files=None, remove=False):
        install_files = install_files or []
        cmap = {}
        for cm, cn in self.iter_collections():
            cmap[cn] = cm
        for fp in install_files:
            if not os.path.isfile(fp):
                self.die("File not found: %s" % fp)
            with open(fp) as f:
                data = ujson.load(f)
            cn = data["$collection"]
            o = self.dereference(cmap[cn], data)
            # Pretty format JSON
            jd = o.to_json()
            path = os.path.join(
                self.get_collection_path(cn),
                o.get_json_path()
            )
            self.stdout.write("[%s] Installing %s\n" % (cn, path))
            safe_rewrite(
                path,
                jd,
                mode=0o644
            )
            if remove:
                os.unlink(fp)

if __name__ == "__main__":
    Command().run()
