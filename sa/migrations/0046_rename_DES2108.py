# -*- coding: utf-8 -*-

from south.db import db

class Migration:

    def forwards(self):
        db.execute("""
        UPDATE sa_managedobject
        SET profile_name='DLink.DES21xx'
        WHERE profile_name='DLink.DES2108'""")

    def backwards(self):
        db.execute("""
        UPDATE sa_managedobject
        SET profile_name='DLink.DES2108'
        WHERE profile_name='DLink.DES21xx'""")
