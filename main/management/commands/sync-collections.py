# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load and syncronize built-in inventory collections
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.nosql import (ListField, EmbeddedDocumentField, ValidationError)
from noc.inv.models import *
from noc.fm.models import *
from noc.lib.debug import error_report
from noc.lib.serialize import json_decode


class CollectionSync:
    def __init__(self, app, name, doc, paths=None):
        self.app = app
        self.name = name
        self.doc = doc
        self.builtin_ids = set()  # existing builtin ids
        self.unique = set()  # unique fields
        self.ref_cache = {}  # model -> field -> key -> value
        self.paths = paths
        if paths is None:
            self.paths = []
            # Look  <app>/collections/<name>/ tree for JSON files
            for dirpath, dirnames, files in os.walk(os.path.join(self.app,
                                                "collections", self.name)):
                for f in files:
                    if f.startswith(".") or not f.endswith(".json"):
                        continue
                    self.paths += [os.path.join(dirpath, f)]

    def get_data(self):
        for path in self.paths:
            with open(path, "r") as jf:
                try:
                    data = json_decode(jf.read())
                except ValueError, why:
                    self.die("JSON error in %s: %s" % (path, why))
            # Data must be either dict or list
            if type(data) == type({}):
                # Convert dict to list
                data = [data]
            if type(data) != type([]):
                self.die("Invalid JSON data type: %s" % type(data))
            for d in data:
                yield d

    def log(self, msg):
        print "    " + msg
    
    def die(self, msg):
        raise CommandError("noc.%s: %s" % (self.name, msg))

    def get_item_label(self, d):
        return ", ".join([u"%s = '%s'" % (u, d[u])
                          for u in self.unique if u in d])

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

    def sync_item(self, d, allow_partial=True):
        changed = False
        created = False
        partial = False
        # Forcefully set is_builtin
        d["is_builtin"] = True
        # Build keys for lookup
        sk = [dict([(u, d[u]) for u in self.unique if u in d])]
        # Get aliases
        if "__aliases" in d:
            for a in d["__aliases"]:
                sk = [dict([(u, a[u]) for u in self.unique if u in a])] + sk                
            del d["__aliases"]
        # Find existing record
        for k in sk:
            obj = self.doc.objects.filter(**k).first()
            if obj:
                break
        if not obj:
            # Create record if not found
            obj = self.doc()
            created = True
        # Compare attributes
        for i, v in d.items():
            i = str(i)
            # Ignore id field
            if i == "id":
                continue
            # Dereference ref_field__field lookups
            if "__" in i and not i.startswith("__"):
                i, f = i.split("__")
                if i not in self.doc._fields:
                    self.die("Invalid lookup field: %s" % i)
                ref = self.doc._fields[i].document_type
                v = self.lookup(ref, f, v)
                cv = getattr(obj, i)
                if cv is None or cv.id != v.id:
                    changed = True
                    setattr(obj, i, v)
                continue
            # Process fields
            try:
                field = self.doc._fields[i]
            except KeyError:
                self.die("Unknown field: '%s'" % i)
            if (type(field) == ListField and
                isinstance(field.field, EmbeddedDocumentField)):
                # ListField(EmbeddedDocumentField(...))
                v = []
                edoc = field.field.document_type
                for dd in d[i]:
                    for ii in dd.keys():
                        if "__" in ii and not ii.startswith("__"):
                            vv = dd[ii]
                            ii, f = ii.split("__")
                            ref = edoc._fields[ii].document_type
                            if allow_partial and self.doc == ref:
                                # Circular reference
                                # Can be unresolved
                                # for this moment
                                try:
                                    dd[ii] = self.lookup(ref, f, vv)
                                except CommandError:
                                    # Try to skip and resolve later
                                    partial = True
                                    continue
                            else:
                                dd[ii] = self.lookup(ref, f, vv)
                    dd = dict([(str(x), y) for x, y in dd.items()])
                    v += [edoc(**dd)]
                if getattr(obj, i) != v:
                    changed = True
                    if allow_partial:
                        # Check List Field is valid
                        # and has all resolved referencies
                        try:
                            field.validate(v)
                        except ValidationError:
                            partial = True
                            continue
                    setattr(obj, i, v)
            elif getattr(obj, i) != v:
                # Other types
                changed = True
                setattr(obj, i, v)
        # Look for deleted list fields
        for f in (set(obj._fields) - set(d)):
            if getattr(obj, f) and type(obj._fields[f]) == ListField:
                setattr(obj, f, None)
                changed = True
        # Save and report changes if exists
        if created:
            self.log("Creating: %s" % unicode(obj))
            obj.save()
        elif changed:
            self.log("Updating: %s" % unicode(obj))
            obj.save()
        return str(obj.id), partial

    def sync(self):
        print "Syncing noc.%s:" % self.name
        # Get builtin ids
        self.builtin_ids = set([str(o.id) for o
                                in self.doc.objects.filter(is_builtin=True)])
        # Define set of unique fields
        self.unique = set()
        for index in self.doc._meta["unique_indexes"]:
            for f, flag in index:
                self.unique.add(f)
        # Sync items
        retry = []
        for d in self.get_data():
            item_id, to_retry = self.sync_item(d, True)
            try:
                self.builtin_ids.remove(item_id)
            except KeyError:
                pass
            if to_retry:
                retry += [d]
        # Retry circular references
        for d in retry:
            self.log("Refining: %s" % self.get_item_label(d))
            item_id, to_retry = self.sync_item(d, False)
            if to_retry:
                self.die("Unable to resolve circular reference for %s" % (
                    self.get_item_label(d)))
        # Remove obsolete builtins
        if self.builtin_ids:
            for o in self.doc.objects.filter(id__in=self.builtin_ids):
                self.log("Removing: %s" % unicode(o))
                o.delete()


class Command(BaseCommand):
    help = "Syncronize built-in inventory collections"

    collections = [
        ("inv", [
            # Inventory
            # ("vendors", Vendor),
            # ("modelinterfaces", ModelInterface),
            ("connectiontypes", ConnectionType),
            ("connectionrules", ConnectionRule),
            ("objectmodels", ObjectModel)
        ]),
        ("fm", [
            # Fault management
            ("oidaliases", OIDAlias),
            ("syntaxaliases", SyntaxAlias),
            ("mibaliases", MIBAlias),
            ("mibpreferences", MIBPreference),
            ("enumerations", Enumeration),
            ("alarmseverities", AlarmSeverity),
            ("alarmclasses", AlarmClass),
            ("eventclasses", EventClass),
            ("eventclassificationrules", EventClassificationRule),
            ("cloneclassificationrules", CloneClassificationRule)
        ])
    ]

    def handle(self, *args, **options):
        try:
            if len(args) > 0:
                name = args[0]
                if "." not in name:
                    raise CommandError("Invalid collection name: %s" % name)
                app, c = name.split(".", 1)
                a = None
                for ad in self.collections:
                    if ad[0] == app:
                        for cn, doc in ad[1]:
                            if cn == c:
                                a = (app, cn, doc)
                                break
                        if a:
                            break
                if not a:
                    raise CommandError("Invalid collection: %s" % name)
                CollectionSync(*a).sync()
            else:
                # Sync all collections
                for app, collections in self.collections:
                    for collection, doc in collections:
                        CollectionSync(app, collection, doc).sync()
        except CommandError, why:
            raise CommandError(why)
        except:
            error_report()
