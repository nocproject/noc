# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# alter type
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
        db.drop_column("vc_vc", "type_id")
        db.execute("ALTER TABLE vc_vcdomain ALTER COLUMN type_id SET NOT NULL")

    def backwards(self):
        pass
