# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.vc.models import *

class Migration:
    
    def forwards(self, orm):
        db.drop_column("vc_vc","type_id")
        db.execute("ALTER TABLE vc_vcdomain ALTER COLUMN type_id SET NOT NULL")    
    
    def backwards(self, orm):
        "Write your backwards migration here"
