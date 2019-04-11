# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# no category
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
        db.delete_table("kb_kbentrytemplate_categories")
        db.delete_table("kb_kbentry_categories")
        db.delete_table("kb_kbcategory")

    def backwards(self):
        pass
