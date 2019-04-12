# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# set user is_staff
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
        db.execute("UPDATE auth_user SET is_staff=TRUE WHERE is_staff=FALSE")

    def backwards(self):
        pass
