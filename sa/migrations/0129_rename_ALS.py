# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='Alsitec.7200' WHERE profile_name LIKE 'ALS.7200'")

    def backwards(self):
        pass
