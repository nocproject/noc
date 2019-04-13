# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# profilecheckrules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        # Get profile record mappings
        pcoll = get_db()["noc.profiles"]
        pcrcoll = get_db()["noc.profilecheckrules"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = d["_id"]
        # Update
        for p in pmap:
            pcrcoll.update_many({"profile": p}, {"$set": {"profile": pmap[p]}})

    def backwards(self):
        pass
