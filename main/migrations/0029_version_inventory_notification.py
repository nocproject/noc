# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["sa.version_inventory"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["sa.version_inventory"])
    
    def backwards(self):
        "Write your backwards migration here"
