# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='NSN.hiX56xx' WHERE profile_name='Siemens.HIX5630'")

    def backwards(self):
        pass
