# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectselector finish tags migration
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
        # Drop old tags
        db.drop_column("sa_managedobjectselector", "filter_tags")
        # Rename new tags
        db.rename_column("sa_managedobjectselector", "tmp_filter_tags", "filter_tags")

    def backwards(self):
        pass
