# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.dns.models import *

class Migration:
    def forwards(self):
        NotificationGroup = db.mock_model(model_name="NotificationGroup",
            db_table="main_notificationgroup", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        db.add_column("dns_dnszoneprofile", "notification_group",
            models.ForeignKey(NotificationGroup, blank=True, null=True))
        db.add_column("dns_dnszone", "notification_group",
            models.ForeignKey(NotificationGroup, blank=True, null=True))
    
    def backwards(self):
        db.delete_column("dns_dnszoneprofile", "notification_group_id")
        db.delete_column("dns_dnszone", "notification_group_id")
    
