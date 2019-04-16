# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# merge Dlink
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
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DxS' WHERE profile_name LIKE 'DLink.D_S3xxx'")

    def backwards(self):
        pass
