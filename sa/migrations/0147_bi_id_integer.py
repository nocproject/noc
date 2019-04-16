# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# bi_id integer
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
        db.execute("UPDATE sa_managedobject SET bi_id=NULL")
        db.execute("ALTER TABLE sa_managedobject ALTER COLUMN bi_id TYPE bigint")
        db.execute("UPDATE sa_administrativedomain SET bi_id=NULL")
        db.execute("ALTER TABLE sa_administrativedomain ALTER COLUMN bi_id TYPE bigint")
        db.execute("UPDATE sa_authprofile SET bi_id=NULL")
        db.execute("ALTER TABLE sa_authprofile ALTER COLUMN bi_id TYPE bigint")
        db.execute("UPDATE sa_terminationgroup SET bi_id=NULL")
        db.execute("ALTER TABLE sa_terminationgroup ALTER COLUMN bi_id TYPE bigint")
        db.execute("UPDATE sa_managedobjectprofile SET bi_id=NULL")
        db.execute("ALTER TABLE sa_managedobjectprofile ALTER COLUMN bi_id TYPE bigint")

    def backwards(self):
        db.execute("UPDATE sa_managedobject SET bi_id=NULL")
        db.execute("ALTER TABLE sa_managedobject ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("UPDATE sa_administrativedomain SET bi_id=NULL")
        db.execute("ALTER TABLE sa_administrativedomain ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("UPDATE sa_authprofile SET bi_id=NULL")
        db.execute("ALTER TABLE sa_authprofile ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("UPDATE sa_terminationgroup SET bi_id=NULL")
        db.execute("ALTER TABLE sa_terminationgroup ALTER COLUMN bi_id TYPE decimal(20,0)")
        db.execute("UPDATE sa_managedobjectprofile SET bi_id=NULL")
        db.execute("ALTER TABLE sa_managedobjectprofile ALTER COLUMN bi_id TYPE decimal(20,0)")
