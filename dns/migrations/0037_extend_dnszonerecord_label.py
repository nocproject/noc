# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# extend dnszonerecord label
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
        db.execute("ALTER TABLE dns_dnszonerecord ALTER name TYPE VARCHAR(64)")

    def backwards(self):
        db.execute("ALTER TABLE dns_dnszonerecord ALTER name TYPE VARCHAR(32)")
