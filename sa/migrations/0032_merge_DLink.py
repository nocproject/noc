# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DxS' WHERE profile_name LIKE 'DLink.D_S3xxx'")

    def backwards(self):
        pass
