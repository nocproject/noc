# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
    
    def forwards(self):
        db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(75)")
    
    def backwards(self):
        db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(30)")
