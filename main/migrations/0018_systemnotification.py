# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    
    def forwards(self):
        NotificationGroup = db.mock_model(model_name='NotificationGroup', db_table='main_notificationgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Adding model 'SystemNotification'
        db.create_table('main_systemnotification', (
            ('notification_group', models.ForeignKey(NotificationGroup, null=True, verbose_name="Notification Group", blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField("Name", unique=True, max_length=64)),
        ))
        db.send_create_signal('main', ['SystemNotification'])
    
    def backwards(self):
        # Deleting model 'SystemNotification'
        db.delete_table('main_systemnotification')