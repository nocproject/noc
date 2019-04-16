# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# event indexes
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
        db.create_index("fm_event", ["status"])
        db.create_index("fm_event", ["timestamp"])

    def backwards(self):
        db.delete_index("fm_event", ["status"])
        db.delete_index("fm_event", ["timestamp"])
