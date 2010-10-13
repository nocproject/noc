# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["ip.sync_macs"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["ip.sync_macs"])
    
    def backwards(self):
        "Write your backwards migration here"
