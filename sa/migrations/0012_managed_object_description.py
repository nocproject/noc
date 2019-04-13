# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject description
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
        db.rename_column("sa_managedobject", "location", "description")

    def backwards(self):
        db.rename_column("sa_managedobject", "description", "location")
