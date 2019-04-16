# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# bi_id decimal
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
        db.execute("ALTER TABLE sa_managedobject ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("ALTER TABLE sa_administrativedomain ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("ALTER TABLE sa_authprofile ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("ALTER TABLE sa_terminationgroup ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("ALTER TABLE sa_managedobjectprofile ALTER COLUMN bi_id TYPE decimal(20,0)")

    def backwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER COLUMN bi_id TYPE int")
        db.execute("ALTER TABLE sa_administrativedomain ALTER COLUMN bi_id TYPE int")
        db.execute("ALTER TABLE sa_authprofile ALTER COLUMN bi_id TYPE int")
        db.execute("ALTER TABLE sa_terminationgroup ALTER COLUMN bi_id TYPE int")
        db.execute("ALTER TABLE sa_managedobjectprofile ALTER COLUMN bi_id TYPE int")
