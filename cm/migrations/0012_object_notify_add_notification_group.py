# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from django.db import models

class Migration:
    depends_on=(
        ("main","0017_initial_userprofilecontacts"),
    )
    def forwards(self):
        NotificationGroup = db.mock_model(model_name='NotificationGroup', db_table='main_notificationgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("cm_objectnotify","notification_group",models.ForeignKey(NotificationGroup,verbose_name="Notification Group",null=True,blank=True))
    
    def backwards(self):
        db.drop_column("cm_objectnotify","notification_group")
