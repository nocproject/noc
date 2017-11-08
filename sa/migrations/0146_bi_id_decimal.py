# -*- coding: utf-8 -*-
from south.db import db


class Migration:
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
