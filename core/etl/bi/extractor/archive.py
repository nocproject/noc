# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ArchivingExtractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict
# Third-party modules
from jinja2 import Template
# NOC modules
from noc.lib.nosql import get_db
from .base import BaseExtractor


class ArchivingExtractor(BaseExtractor):
    enable_archive = False
    archive_batch_limit = 1000
    archive_collection_template = None

    def clean(self):
        if self.enable_archive:
            self.archive()
        super(ArchivingExtractor, self).clean()

    def iter_archived_items(self):
        """
        Generator yielding documents to be archived
        :return:
        """
        raise StopIteration()

    def archive(self):
        """
        Move data to archive collection
        :return:
        """
        def spool(collection_name):
            coll = db[collection_name]
            coll.insert_many(data[collection_name])

        db = get_db()
        # Compile name template
        tpl = Template(self.archive_collection_template)
        # collection name -> data
        data = defaultdict(list)
        # Collect data and spool full batches
        for d in self.iter_archived_items():
            cname = str(tpl.render({
                "doc": d
            }))
            data[cname] += [d]
            if len(data[cname]) >= self.archive_batch_limit:
                spool(cname)
                data[cname] = []
        # Spool remaining incomplete batches
        for cname in data:
            if data[cname]:
                spool(cname)
