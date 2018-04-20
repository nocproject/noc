# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        NotificationGroup = db.mock_model(model_name="NotificationGroup",
            db_table="main_notificationgroup", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        db.add_column("dns_dnszoneprofile", "notification_group",
            models.ForeignKey(NotificationGroup, blank=True, null=True))
        db.add_column("dns_dnszone", "notification_group",
            models.ForeignKey(NotificationGroup, blank=True, null=True))
<<<<<<< HEAD

    def backwards(self):
        db.delete_column("dns_dnszoneprofile", "notification_group_id")
        db.delete_column("dns_dnszone", "notification_group_id")

=======
    
    def backwards(self):
        db.delete_column("dns_dnszoneprofile", "notification_group_id")
        db.delete_column("dns_dnszone", "notification_group_id")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
