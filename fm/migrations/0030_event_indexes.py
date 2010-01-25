# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.fm.models import *

class Migration:
    
    def forwards(self, orm):
        db.create_index("fm_event",["status"])
        db.create_index("fm_event",["timestamp"])
    
    
    def backwards(self, orm):
        db.delete_index("fm_event",["status"])
        db.delete_index("fm_event",["timestamp"])
    
    models = {
    }
    
    complete_apps = ['fm']
