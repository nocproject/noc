# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# enlarge username
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
        db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(75)")

    def backwards(self):
        db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(30)")
