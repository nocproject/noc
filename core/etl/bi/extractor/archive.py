# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ArchivingExtractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import, print_function
from collections import defaultdict
# Third-party modules
import bisect
import pymongo
from pymongo.errors import BulkWriteError
from jinja2 import Template
# NOC modules
from noc.lib.nosql import get_db
from .base import BaseExtractor


class ArchivingExtractor(BaseExtractor):
    enable_archive = False
    use_archive = False
    archive_batch_limit = 1000
    archive_collection_template = None
    archive_collection_prefix = "alarms"
    archive_db = get_db()
    archive_meta = {}
    archive_intervals = {}

    def clean(self, force=False):
        if self.enable_archive:
            self.archive()
        super(ArchivingExtractor, self).clean()

    def get_archived_template(self):
        # "alarms.{{doc[\"clear_timestamp\"].strftime(\"y%Yw%W\")}}"
        # print(self.archive_collection_template)
        template = "%s.%s" % (self.name, self.archive_collection_template)
        return Template(template)

    def iter_archived_items(self):
        """
        Generator yielding documents to be archived
        :return:
        """
        raise StopIteration()

    def iter_archived_collections(self):
        """
        Generator yielding archived collection names
        :return:
        :rtype: str
        """
        for c in self.archive_db.list_collection_names():
            if not c.startswith(self.archive_collection_prefix):
                continue
            yield c

    def calculate_meta(self, collection_name):
        """
        Calculate Meta Information about archived collection
        :param collection_name:
        :return:
        :rtype: dict
        """
        coll = self.archive_db.get_collection(collection_name)
        start_document = coll.find_one(sort=([("clear_timestamp", pymongo.ASCENDING)]),
                                       projection={"clear_timestamp": 1})
        end_document = coll.find_one(sort=([("clear_timestamp", pymongo.DESCENDING)]),
                                     projection={"clear_timestamp": 1})
        return {"name": self.name,
                "first_record_ts": start_document["clear_timestamp"],  # Timestamp on first record
                "last_record_ts": end_document["clear_timestamp"],  # Timestamp on last record
                "record_count": coll.count({"clear_timestamp": {"$exists": True}})}   # Record count

    def fill_meta(self):
        for collection_name in self.iter_archived_collections():
            coll = self.archive_db.get_collection(collection_name)
            meta_doc = coll.find_one({"type": "metadata"})
            if not meta_doc:
                meta_doc = self.calculate_meta(collection_name)
            self.archive_meta[collection_name] = meta_doc
            self.archive_intervals[meta_doc["last_record_ts"]] = collection_name

    def find_archived_collections(self, start, stop):
        if not self.archive_intervals:
            self.fill_meta()
        dates = sorted(self.archive_intervals)
        lower = bisect.bisect_right(dates, start)
        upper = bisect.bisect_right(dates, stop) + 1
        if lower + 1 > len(dates):
            return []
        return [self.archive_intervals[d] for d in dates[lower:upper]]

    def archive(self):
        """
        Move data to archive collection
        :return:
        """
        def spool(collection_name):
            coll = db[collection_name]
            try:
                r = coll.insert_many(data[collection_name])
            except BulkWriteError as e:
                print(e.details)
                return None
            return r

        db = get_db()
        # Compile name template
        tpl = self.get_archived_template()
        # collection name -> data
        data = defaultdict(list)
        # Collect data and spool full batches
        for d in self.iter_archived_items():
            cname = str(tpl.render({
                "doc": d
            }))
            data[cname] += [d]
            if len(data[cname]) >= self.archive_batch_limit:
                result = spool(cname)
                if result:
                    data[cname] = []
                else:
                    break
        # Spool remaining incomplete batches
        for cname in data:
            if data[cname]:
                spool(cname)
