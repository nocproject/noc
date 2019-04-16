# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject set profile
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
        r = db.execute("SELECT id FROM sa_managedobjectprofile WHERE name='default'")
        p_id = r[0][0]
        db.execute("UPDATE sa_managedobject SET object_profile_id = %s", [p_id])

    def backwards(self):
        pass
