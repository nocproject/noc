# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rename rr type is_visible
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
        db.rename_column("dns_dnszonerecordtype", "is_visible", "is_active")

    def backwards(self):
        db.rename_column("dns_dnszonerecordtype", "is_active", "is_visible")
