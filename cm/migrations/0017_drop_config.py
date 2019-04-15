# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# drop config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    depends_on = [("sa", "0077_drop_repo_path")]

    def forwards(self):
        db.drop_table("cm_config")

    def backwards(self):
        pass
