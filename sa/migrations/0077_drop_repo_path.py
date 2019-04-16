# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# drop repo path
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
        db.drop_column("sa_managedobject", "is_configuration_managed")
        db.drop_column("sa_managedobject", "repo_path")

    def backwards(self):
        pass
