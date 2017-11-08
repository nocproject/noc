# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.execute("ALTER TABLE sa_administrativedomain ALTER name TYPE VARCHAR(255)")

    def backwards(self):
        db.execute("ALTER TABLE sa_administrativedomain ALTER name TYPE VARCHAR(32)")
