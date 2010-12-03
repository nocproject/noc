# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
    
    def forwards(self):
        db.execute("UPDATE auth_user SET is_staff=TRUE WHERE is_staff=FALSE")
        
    def backwards(self):
        "Write your backwards migration here"
