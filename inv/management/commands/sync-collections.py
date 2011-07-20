# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load and syncronize built-in inventory collections
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import os
## Django modules
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson
## NOC modules
from noc.inv.models import *
from noc.fm.models import *
from noc.lib.debug import error_report


class Command(BaseCommand):
    help = "Syncronize built-in inventory collections"

    collections = [
        #("inv", [
        #    # Inventory
        #    ("sockets", Socket),
        #    ("vendors", Vendor),
        #    ("models", Model)
        #]),
        ("fm", [
            # Fault management
            ("alarmseverities", AlarmSeverity),
            ("alarmclasses", AlarmClass),
            ("eventclasses", EventClass),
            ("eventclassificationrules", EventClassificationRule)
            ])
    ]

    def handle(self, *args, **options):
        try:
            self._handle(*args, **options)
        except:
            error_report()

    def _handle(self, *args, **options):
        def lookup(doc, field, key):
            field = str(field)
            if ref not in ref_cache:
                ref_cache[doc] = {field: {}}
            if field not in ref_cache[doc]:
                ref_cache[doc][field] = {}
            if key in ref_cache[doc][field]:
                return ref_cache[doc][field][key]
            else:
                v = ref.objects.get(**{field: key})
                if not v:
                    raise CommandError("%s: lookup for %s.%s == '%s' has been failed" % (
                        collection, doc._meta["collection"], field, key))
                ref_cache[doc][field][key] = v
                return v
        
        def fail(collection, msg):
            if not collection.startswith("noc."):
                collection = "noc." + collection
            raise CommandError("%s: %s" % (collection, msg))
            
        # For each system collection
        ref_cache = {}  # model -> field -> key -> value
        for app, collections in self.collections:
            for collection, doc in collections:
                c_root = os.path.join(app, "collections")
                print "Syncing noc.%s" % collection
                builtin_ids = set([str(o._id) for o
                                   in doc.objects.filter(is_builtin=True)])
                # Define set of unique fields
                unique = set()
                for index in doc._meta["unique_indexes"]:
                    for f, flag in index:
                        unique.add(f)
                # Scan for json
                for dirpath, dirnames, files in os.walk(os.path.join(c_root,
                                                                     collection)):
                    for f in files:
                        if f.startswith(".") or not f.endswith(".json"):
                            continue
                        # Load json
                        path = os.path.join(dirpath, f)
                        with open(path, "r") as jf:
                            try:
                                data = simplejson.JSONDecoder().decode(jf.read())
                            except ValueError, why:
                                fail(collection, "JSON error in %s: %s" % (path,
                                                                           why))
                                # Data must be either dict or list
                        if type(data) == type({}):
                            # Convert dict to list
                            data = [data]
                        if type(data) != type([]):
                            fail(collection,
                                 "invalid JSON data type: %s" % type(data))
                        # Process data items (dicts)
                        for d in data:
                            changed = False
                            created = False
                            # Forcefully set is_builtin
                            d["is_builtin"] = True
                            # Build key for lookup
                            k = dict([(u, d[u]) for u in unique if u in d])
                            # Find existing record
                            obj = doc.objects.filter(**k).first()
                            if not obj:
                                # Create record if not found
                                obj = doc()
                                created = True
                            else:
                                try:
                                    builtin_ids.remove(str(obj._id))
                                except KeyError:
                                    pass
                            # Compare attributes
                            for i, v in d.items():
                                i = str(i)
                                # Ignore id field
                                if i == "id":
                                    continue
                                # Dereference ref_field__field lookups
                                if "__" in i and not i.startswith("__"):
                                    i, f = i.split("__")
                                    if i not in doc._fields:
                                        fail("Invalid lookup field: %s" % i)
                                    ref = doc._fields[i].document_type
                                    v = lookup(ref, f, v)
                                    cv = getattr(obj, i)
                                    if cv is None or cv.id != v.id:
                                        changed = True
                                        setattr(obj, i, v)
                                    continue
                                # Process fields
                                field = doc._fields[i]
                                if (type(field) == ListField and
                                    isinstance(field.field, EmbeddedDocumentField)):
                                    # ListField(EmbeddedDocumentField(...))
                                    v = []
                                    edoc = field.field.document_type
                                    for dd in d[i]:
                                        for ii in dd.keys():
                                            if "__" in ii and not ii.startswith("__"):
                                                vv = dd.pop(ii)
                                                ii, f = ii.split("__")
                                                ref = edoc._fields[ii].document_type
                                                dd[ii] = lookup(ref, f, vv)
                                        dd = dict([(str(x), y) for x, y in dd.items()])
                                        v += [edoc(**dd)]
                                    if getattr(obj, i) != v:
                                        changed = True
                                        setattr(obj, i, v)
                                elif getattr(obj, i) != v:
                                    # Other types
                                    changed = True
                                    setattr(obj, i, v)
                            # Save and report changes if exists
                            if created or changed:
                                t = ", ".join([u"%s = '%s'" % (x, y)
                                               for x, y in k.items()])
                                print "    %s in noc.%s: %s" % (
                                    "Creating" if created else "Updating",
                                    collection,
                                    t
                                )
                                obj.save()
                # Remove hanging builtins
                if builtin_ids:
                    for o in doc.objects.filter(id__in=builtin_ids):
                        print "    Removing from noc.%s: %s" % (collection, unicode(o))
                        o.delete()
