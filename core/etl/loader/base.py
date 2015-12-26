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
## Python modules
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

    fields = []

    PREFIX = "var/import"
    rx_archive = re.compile(
        "^import-\d{4}(?:-\d{2}){5}.csv.gz$"
    )

    def __init__(self, system):
        self.system = system
        self.logger = PrefixLoggerAdapter(
            logger, "%s][%s" % (system, self.name)
        )
        self.import_dir = os.path.join(self.PREFIX, system, self.name)
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
                              for n in self.fields)  # field name -> clean function
        if self.model:
            if isinstance(self.model._meta, dict):
                self.update_document_clean_map()

    def load_mappings(self):
        """
        Load mappings file
        """
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
                    o = getnext(o)

    def load(self):
        """
        Import new data
        """
        self.logger.info("Importing")
        ns = self.get_new_state()
        if not ns:
            self.logger.info("No new state, skipping")
            return
        current_state = csv.reader(self.get_current_state())
        new_state = csv.reader(ns)
        for o, n in self.diff(current_state, new_state):
            if o is None and n:
                self.on_add(n)
            elif o and n is None:
                self.on_delete(o)
            else:
                self.on_change(o, n)
        self.logger.info(
            "Summary: %d new, %d changed, %d removed",
            self.c_add, self.c_change, self.c_delete
        )
        self.save_state()

    @classmethod
    def load_all(cls, system):
        """
        Load all data from system
        """
        from loader import loader

        # @todo: Loader dependency
        prefix = os.path.join(cls.PREFIX, system)
        if not os.path.isdir(prefix):
            logger.error("Cannot open directory: %s", prefix)
            return 1
        for d in os.listdir(prefix):
            if os.path.isdir(os.path.join(prefix, d)):
                lc = loader.get_loader(d)
                if not lc:
                    continue
                lc(system).load()
        return 0

    def on_add(self, row):
        """
        Create new record
        """
        self.logger.debug("Add: %s", "|".join(row))
        self.c_add += 1
        v = self.clean(row)
        # @todo: Check record is already exists
        if self.fields[0] in v:
            del v[self.fields[0]]
        o = self.model(**v)
        o.save()
        self.set_mappings(row[0], o.id)

    def on_change(self, o, n):
        """
        Create change record
        """
        self.logger.debug("Change: %s", "|".join(n))
        self.c_change += 1
        obj = self.model.objects.get(pk=self.mappings[n[0]])
        v = self.clean(n)
        for fn, (ov, nv) in zip(self.fields[1:], zip(o[1:], n[1:])):
            if ov != nv:
                self.logger.debug("   %s: %s -> %s", fn, ov, nv)
                setattr(obj, fn, v[fn])
        obj.save()

    def on_delete(self, row):
        """
        Delete record
        """
        self.logger.debug("Delete: %s", "|".join(row))
        self.c_delete += 1
        obj = self.model.objects.get(pk=self.mappings[row[0]])
        obj.delete()

    def save_state(self):
        """
        Save current state
        """
        t = time.localtime()
        archive_path = os.path.join(
            self.archive_dir,
            "import-%04d-%02d-%02d-%02d-%02d-%02d.csv.gz" % tuple(t[:6])
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
            return value
        else:
            return None

    def clean_bool(self, value):
        if value == "":
            return None
        value = value.lower()
        return value in ("t", "true", "y", "yes")

    def clean_plain_reference(self, mappings, r_model, value):
        if not value:
            return None
        else:
            # @todo: Get proper mappings
            value = mappings[value]
            return r_model.objects.get(id=value)

    def set_mappings(self, rv, lv):
        self.logger.debug("Set mapping remote: %s, local: %s", rv, lv)
        self.mappings[str(rv)] = str(lv)

    def update_document_clean_map(self):
        from mongoengine.fields import BooleanField, IntField, FloatField
        from noc.lib.nosql import PlainReferenceField

        for fn, ft in self.model._fields.iteritems():
            if fn not in self.clean_map:
                continue
            if isinstance(ft, BooleanField):
                self.clean_map[fn] = self.clean_bool
            elif isinstance(ft, PlainReferenceField):
                self.clean_map[fn] = functools.partial(
                    self.clean_plain_reference,
                    self.mappings, ft.document_type
                )
