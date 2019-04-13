# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# activator drop ip
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
        db.delete_column("sa_activator", "ip")
        db.delete_column("sa_activator", "to_ip")
        db.execute("ALTER TABLE sa_activator ALTER prefix_table_id SET NOT NULL")

    def backwards(self):
        pass
