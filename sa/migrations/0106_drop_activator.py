# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# drop activator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    depends_on = [("main", "0033_shard")]

    def forwards(self):
        db.delete_column("sa_managedobjectselector", "filter_activator_id")
        db.drop_table("sa_activator")
        db.drop_table("sa_collector")
        db.drop_table("main_shard")

    def backwards(self):
        pass
