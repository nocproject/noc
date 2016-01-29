# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Data Loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import gzip
import re
import StringIO
import csv
import time
import shutil
import functools
## NOC modules
from noc.lib.log import PrefixLoggerAdapter
from noc.lib.fileutils import safe_rewrite

logger = logging.getLogger(__name__)


class BaseLoader(object):
    """
    Import directory structure:
    var/
        import/
            <system name>/
                <loader name>/
                    import.csv[.gz]  -- state to load, can have .gz extension
                    mapping.csv -- ID mappings
                    archive/
                        import-YYYY-MM-DD-HH-MM-SS.csv.gz -- imported state

    Import file format: CSV, unix end of lines, UTF-8, comma-separated
    First column - record id in the terms of connected system,
    other columns must be defined in *fields* variable.

    File must be sorted by first field either as string or as numbers,
    sort order must not be changed.

    mappings.csv - CSV, unix end of lines, UTF-8 comma separated
    mappings of ID between NOC and remote system. Populated by loader
    automatically.

    :param fields: List of either field names or tuple of
        (field name, related loader name)
    """
    # Loader name
    name = None
    # Loader model
    model = None
    # Mapped fields
    mapped_fields = {}

    fields = []

    # List of tags to add to the created records
    tags = []

    PREFIX = "var/import"
    rx_archive = re.compile(
            "^import-\d{4}(?:-\d{2}){5}.csv.gz$"
    )

    # Discard records which cannot be dereferenced
    discard_deferred = False

    REPORT_INTERVAL = 1000

    class Deferred(Exception):
        pass

    def __init__(self, chain):
        self.chain = chain
        self.system = chain.system
        self.logger = PrefixLoggerAdapter(
                logger, "%s][%s" % (self.system, self.name)
        )
        self.import_dir = os.path.join(self.PREFIX,
                                       self.system, self.name)
        self.archive_dir = os.path.join(self.import_dir, "archive")
        self.mappings_path = os.path.join(
            self.import_dir,
            "mappings.csv"
        )
        self.mappings = {}
        self.new_state_path = None
        self.c_add = 0
        self.c_change = 0
        self.c_delete = 0
        # Build clean map
        self.clean_map = dict((n, self.clean_str)
                              for n in
                              self.fields)  # field name -> clean function
        self.pending_deletes = []  # (id, string)
        self.tags = []
        if self.is_document:
            if "tags" in self.model._fields:
                self.tags += ["src:%s" % self.system]
        else:
            if any(f for f in self.model._meta.fields if f.name == "tags"):
                self.tags += ["src:%s" % self.system]

    @property
    def is_document(self):
        """
        Returns True if model is Document, False - if Model
        """
        return hasattr(self.model, "_fields")

    def load_mappings(self):
        """
        Load mappings file
        """
        if self.model:
            if self.is_document:
                self.update_document_clean_map()
            else:
                self.update_model_clean_map()
        if not os.path.exists(self.mappings_path):
            return
        self.logger.info("Loading mappings from %s", self.mappings_path)
        with open(self.mappings_path) as f:
            reader = csv.reader(f)
            for k, v in reader:
                self.mappings[k] = v
        self.logger.info("%d mappings restored", len(self.mappings))

    def get_new_state(self):
        """
        Returns file object of new state, or None when not present
        """
        # Try import.csv
        path = os.path.join(self.import_dir, "import.csv")
        if os.path.isfile(path):
            logger.info("Loading from %s", path)
            self.new_state_path = path
            return open(path, "r")
        # Try import.csv.gz
        path += ".gz"
        if os.path.isfile(path):
            logger.info("Loading from %s", path)
            self.new_state_path = path
            return gzip.GzipFile(path, "r")
        # No data to import
        return None

    def get_current_state(self):
        """
        Returns file object of current state or None
        """
        self.load_mappings()
        if not os.path.isdir(self.archive_dir):
            self.logger.info("Creating archive directory: %s",
                             self.archive_dir)
            try:
                os.mkdir(self.archive_dir)
            except OSError, why:
                self.logger.error("Failed to create directory: %s (%s)",
                                  self.archive_dir, why)
                # @todo: Die
        fn = sorted(
                f for f in os.listdir(self.archive_dir)
                if self.rx_archive.match(f)
        )
        if fn:
            path = os.path.join(self.archive_dir, fn[-1])
            logger.info("Current state from %s", path)
            return gzip.GzipFile(path, "r")
        # No current state
        return StringIO.StringIO("")

    def diff(self, old, new):
        """
        Compare old and new CSV files and yield pair of matches
        * old, new -- when changed
        * old, None -- when removed
        * None, new -- when added
        """

        def getnext(g):
            try:
                return g.next()
            except StopIteration:
                return None

        o = getnext(old)
        n = getnext(new)
        while o or n:
            if not o:
                # New
                yield None, n
                n = getnext(new)
            elif not n:
                # Removed
                yield o, None
                o = getnext(old)
            else:
                if n[0] == o[0]:
                    # Changed
                    if n != o:
                        yield o, n
                    n = getnext(new)
                    o = getnext(old)
                elif n[0] < o[0]:
                    # Added
                    yield None, n
                    n = getnext(new)
                else:
                    # Removed
                    yield o, None
                    o = getnext(old)

    def load(self):
        """
        Import new data
        """
        self.logger.info("Importing")
        ns = self.get_new_state()
        if not ns:
            self.logger.info("No new state, skipping")
            self.load_mappings()
            return
        current_state = csv.reader(self.get_current_state())
        new_state = csv.reader(ns)
        deferred = []
        for o, n in self.diff(current_state, new_state):
            if o is None and n:
                try:
                    self.on_add(n)
                except self.Deferred:
                    if not self.discard_deferred:
                        deferred += [n]
            elif o and n is None:
                self.on_delete(o)
            else:
                self.on_change(o, n)
            rn = self.c_add + self.c_change + self.c_delete
            if rn > 0 and rn % self.REPORT_INTERVAL == 0:
                self.logger.info("   ... %d records", rn)
        # Load deferred record
        while len(deferred):
            nd = []
            for row in deferred:
                try:
                    self.on_add(row)
                except self.Deferred:
                    deferred += [row]
            if len(nd) == len(deferred):
                raise Exception("Unable to defer references")
            deferred = nd
            rn = self.c_add + self.c_change + self.c_delete
            if rn % self.REPORT_INTERVAL == 0:
                self.logger.info("   ... %d records", rn)

    def create_object(self, v):
        """
        Create object with attributes. Override to save complex
        data structures
        """
        o = self.model(**v)
        if self.tags:
            t = o.tags or []
            o.tags = t + self.tags
        o.save()
        return o

    def change_object(self, object_id, v):
        """
        Change object with attributes
        """
        o = self.model.objects.get(pk=object_id)
        for k, nv in v.iteritems():
            setattr(o, k, nv)
        o.save()
        return o

    def on_add(self, row):
        """
        Create new record
        """
        self.logger.debug("Add: %s", ";".join(row))
        v = self.clean(row)
        self.c_add += 1
        # @todo: Check record is already exists
        if self.fields[0] in v:
            del v[self.fields[0]]
        o = self.create_object(v)
        self.set_mappings(row[0], o.id)

    def on_change(self, o, n):
        """
        Create change record
        """
        self.logger.debug("Change: %s", ";".join(n))
        self.c_change += 1
        v = self.clean(n)
        vv = {}
        for fn, (ov, nv) in zip(self.fields[1:], zip(o[1:], n[1:])):
            if ov != nv:
                self.logger.debug("   %s: %s -> %s", fn, ov, nv)
                vv[fn] = v[fn]
        self.change_object(self.mappings[n[0]], vv)

    def on_delete(self, row):
        """
        Delete record
        """
        self.pending_deletes += [(row[0], ";".join(row))]

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Delete: %s", msg)
            self.c_delete += 1
            obj = self.model.objects.get(pk=self.mappings[r_id])
            obj.delete()
        self.pending_deletes = []

    def save_state(self):
        """
        Save current state
        """
        self.logger.info(
                "Summary: %d new, %d changed, %d removed",
                self.c_add, self.c_change, self.c_delete
        )
        t = time.localtime()
        archive_path = os.path.join(
                self.archive_dir,
                "import-%04d-%02d-%02d-%02d-%02d-%02d.csv.gz" % tuple(
                        t[:6])
        )
        self.logger.info("Moving %s to %s",
                         self.new_state_path, archive_path)
        if self.new_state_path.endswith(".gz"):
            # Simply move the file
            shutil.move(self.new_state_path, archive_path)
        else:
            # Compress the file
            self.logger.info("Compressing")
            with open(self.new_state_path, "r") as s:
                with gzip.open(archive_path, "w") as d:
                    d.write(s.read())
            os.unlink(self.new_state_path)
        self.logger.info("Saving mappings to %s", self.mappings_path)
        mdata = "\n".join("%s,%s" % (k, self.mappings[k])
                          for k in sorted(self.mappings))
        safe_rewrite(self.mappings_path, mdata)

    def clean(self, row):
        """
        Cleanup row and return a dict of field name -> value
        """
        r = dict((k, self.clean_map[k](v))
                 for k, v in zip(self.fields, row))
        return r

    def clean_str(self, value):
        if value:
            if isinstance(value, str):
                return unicode(value, "utf-8")
            elif not isinstance(value, basestring):
                return str(value)
            else:
                return value
        else:
            return None

    def clean_map_str(self, mappings, value):
        value = self.clean_str(value)
        if value:
            try:
                value = mappings[value]
            except KeyError:
                raise self.Deferred
        return value

    def clean_bool(self, value):
        if value == "":
            return None
        try:
            return int(value) != 0
        except ValueError:
            pass
        value = value.lower()
        return value in ("t", "true", "y", "yes")

    def clean_reference(self, mappings, r_model, value):
        if not value:
            return None
        else:
            # @todo: Get proper mappings
            try:
                value = mappings[value]
            except KeyError:
                raise self.Deferred()
            return self.chain.cache[r_model, value]

    def set_mappings(self, rv, lv):
        self.logger.debug("Set mapping remote: %s, local: %s", rv, lv)
        self.mappings[str(rv)] = str(lv)

    def update_document_clean_map(self):
        from mongoengine.fields import (BooleanField, IntField,
                                        FloatField, ReferenceField)
        from noc.lib.nosql import PlainReferenceField

        for fn, ft in self.model._fields.iteritems():
            if fn not in self.clean_map:
                continue
            if isinstance(ft, BooleanField):
                self.clean_map[fn] = self.clean_bool
            elif isinstance(ft, (PlainReferenceField, ReferenceField)):
                if fn in self.mapped_fields:
                    self.clean_map[fn] = functools.partial(
                            self.clean_reference,
                            self.chain.get_mappings(
                                    self.mapped_fields[fn]),
                            ft.document_type
                    )
            elif fn in self.mapped_fields:
                self.clean_map[fn] = functools.partial(
                    self.clean_map_str,
                    self.chain.get_mappings(
                        self.mapped_fields[fn])
                )

    def update_model_clean_map(self):
        from django.db.models import BooleanField, ForeignKey
        from noc.core.model.fields import DocumentReferenceField

        for f in self.model._meta.fields:
            if f.name not in self.clean_map:
                continue
            if isinstance(f, BooleanField):
                self.clean_map[f.name] = self.clean_bool
            elif isinstance(f, DocumentReferenceField):
                if f.name in self.mapped_fields:
                    self.clean_map[f.name] = functools.partial(
                        self.clean_reference,
                        self.chain.get_mappings(
                            self.mapped_fields[f.name]),
                        f.document
                    )
            elif isinstance(f, ForeignKey):
                if f.name in self.mapped_fields:
                    self.clean_map[f.name] = functools.partial(
                        self.clean_reference,
                        self.chain.get_mappings(
                            self.mapped_fields[f.name]),
                        f.rel.to
                    )
            elif f.name in self.mapped_fields:
                self.clean_map[f.name] = functools.partial(
                    self.clean_map_str,
                    self.chain.get_mappings(
                        self.mapped_fields[f.name])
                )

    def check(self, chain):
        self.logger.info("Checking")
        # Get constraints
        if self.is_document:
            # Document
            required_fields = [
                f.name
                for f in self.model._fields.itervalues()
                if f.required or f.unique
            ]
            unique_fields = [
                f.name
                for f in self.model._fields.itervalues()
                if f.unique
            ]
        else:
            # Model
            required_fields = [f.name for f in self.model._meta.fields
                               if not f.blank]
            unique_fields = [f.name for f in self.model._meta.fields
                             if f.unique and
                             f.name != self.model._meta.pk.name]
        if not required_fields and not unique_fields:
            self.logger.info("Nothing to check, skipping")
            return 0
        # Prepare data
        ns = self.get_new_state()
        if not ns:
            self.logger.info("No new state, skipping")
            return 0
        new_state = csv.reader(ns)
        r_index = set(self.fields.index(f) for f in required_fields if f in self.fields)
        u_index = set(self.fields.index(f) for f in unique_fields)
        m_index = set(self.fields.index(f) for f in self.mapped_fields)
        uv = set()
        m_data = {}  # field_number -> set of mapped ids
        # Load mapped ids
        for f in self.mapped_fields:
            l = chain.get_loader(self.mapped_fields[f])
            ms = csv.reader(l.get_new_state())
            m_data[self.fields.index(f)] = set(row[0] for row in ms)
        # Process data
        n_errors = 0
        for row in new_state:
            # Check required fields
            for i in r_index:
                if not row[i]:
                    self.logger.error(
                            "ERROR: Required field #%d(%s) is missed in row: %s",
                            i, self.fields[i], ",".join(row)
                    )
                    n_errors += 1
                    continue
            # Check unique fields
            for i in u_index:
                v = row[i]
                if (i, v) in uv:
                    self.logger.error(
                            "ERROR: Field #%d(%s) value is not unique: %s",
                            i, self.fields[i], ",".join(row)
                    )
                    n_errors += 1
                else:
                    uv.add((i, v))
            # Check mapped fields
            for i in m_index:
                v = row[i]
                if v and v not in m_data[i]:
                    self.logger.error(
                            "ERROR: Field #%d(%s) refers to non-existent record: %s",
                            i, self.fields[i], ",".join(row)
                    )
                    n_errors += 1
        if n_errors:
            self.logger.info("%d errors found", n_errors)
        else:
            self.logger.info("No errors found")
        return n_errors

    def check_diff(self):
        def dump(cmd, row):
            print "%s %s" % (cmd, ",".join(row))

        print "--- %s.%s" % (self.chain.system, self.name)
        ns = self.get_new_state()
        if not ns:
            return
        current_state = csv.reader(self.get_current_state())
        new_state = csv.reader(ns)
        for o, n in self.diff(current_state, new_state):
            if o is None and n:
                dump("+", n)
            elif o and n is None:
                dump("-", o)
            else:
                dump("-", o)
                dump("+", n)
