# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        db.execute("ALTER TABLE sa_useraccess ALTER selector_id SET NOT NULL")
    
    
    def backwards(self):
        "Write your backwards migration here"
