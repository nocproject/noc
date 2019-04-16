# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject path size
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
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(256)")

    def backwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(32)")
