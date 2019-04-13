# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectselector drop repo_path
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
        db.drop_column("sa_managedobjectselector", "filter_repo_path")

    def backwards(self):
        pass
