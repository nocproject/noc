# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
<<<<<<< HEAD
from django.db import models

class Migration:

    def forwards(self):
        db.drop_column("cm_objectnotify","emails")
        db.execute("ALTER TABLE cm_objectnotify ALTER COLUMN notification_group_id SET NOT NULL")


=======
from noc.cm.models import *

class Migration:
    
    def forwards(self):
        db.drop_column("cm_objectnotify","emails")
        db.execute("ALTER TABLE cm_objectnotify ALTER COLUMN notification_group_id SET NOT NULL")
    
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.add_column("cm_objectnotify","emails",models.CharField("Emails",max_length=128))
