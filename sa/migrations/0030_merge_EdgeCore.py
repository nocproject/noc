# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='EdgeCore.ES' WHERE profile_name LIKE 'EdgeCore.ES%%'")

    def backwards(self):
        pass
