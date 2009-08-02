# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.cm.models import *

class Migration:
    
    def forwards(self):
        db.drop_column("cm_objectnotify","emails")
        db.execute("ALTER TABLE cm_objectnotify ALTER COLUMN notification_group_id SET NOT NULL")
    
    
    def backwards(self):
        db.add_column("cm_objectnotify","emails",models.CharField("Emails",max_length=128))
