# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject pool not null
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
        db.execute("ALTER TABLE sa_managedobject ALTER pool SET NOT NULL")

    def backwards(self):
        pass
