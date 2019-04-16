# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# drop cache tables
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.delete_table("peer_prefixlistcache")
        db.delete_table("peer_whoiscache")
        db.delete_table("peer_whoislookup")
        db.delete_table("peer_whoisdatabase")

    def backwards(self):
        pass
