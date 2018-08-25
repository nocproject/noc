# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        handlers = set()
        for h, in db.execute("SELECT DISTINCT config_filter_handler FROM sa_managedobject"):
            if h:
                handlers.add(h)
        for h, in db.execute("SELECT DISTINCT config_diff_filter_handler FROM sa_managedobject"):
            if h:
                handlers.add(h)
        if handlers:
            coll = get_db()["handlers"]
            for h in handlers:
                name = h.split(".")[-2]
                coll.insert({
                    "_id": h,
                    "name": name,
                    "allow_config_filter": True
                })
        handlers = set()
        for h, in db.execute("SELECT DISTINCT config_validation_handler FROM sa_managedobject"):
            if h:
                handlers.add(h)
        if handlers:
            coll = get_db()["handlers"]
            for h in handlers:
                name = h.split(".")[-2]
                coll.insert({
                    "_id": h,
                    "name": name,
                    "allow_config_validation": True
                })

    def backwards(self):
        pass
