# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.create_unique('fm_eventarchivationrule', ['event_class_id', 'action'])
        try:
            db.delete_unique('fm_eventarchivationrule', ['event_class_id'])
        except:
            pass
    
    def backwards(self):
        db.delete_unique('fm_eventarchivationrule', ['event_class_id', 'action'])
        db.create_unique('fm_eventarchivationrule', ['event_class_id'])
        
