# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# administrative domain
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
        db.execute("ALTER TABLE sa_administrativedomain ALTER name TYPE VARCHAR(255)")

    def backwards(self):
        db.execute("ALTER TABLE sa_administrativedomain ALTER name TYPE VARCHAR(32)")
