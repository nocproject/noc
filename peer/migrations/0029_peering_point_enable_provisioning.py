# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *
from noc.main.models import *

class Migration:
    
    def forwards(self):
        NotificationGroup = db.mock_model(model_name='NotificationGroup', db_table='main_notificationgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("peer_peeringpoint","enable_prefix_list_provisioning",models.BooleanField("Enable Prefix-List Provisioning",default=False))
        db.add_column("peer_peeringpoint","prefix_list_notification_group",models.ForeignKey(NotificationGroup,verbose_name="Prefix List Notification Group",null=True,blank=True))
    
    
    def backwards(self):
        db.delete_column("peer_peeringpoint","enable_prefix_list_provisioning")
        db.delete_column("peer_peeringpoint","prefix_list_notification_group")
