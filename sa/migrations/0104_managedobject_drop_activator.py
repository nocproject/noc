# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject drop activator_id
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
        db.delete_column("sa_managedobject", "activator_id")

    def backwards(self):
        pass
