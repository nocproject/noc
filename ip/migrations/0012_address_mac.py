# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.ip.models import *

class Migration:
    depends_on=(
        ("sa","0007_managed_object"),
    )
    def forwards(self):
        ManagedObject=db.mock_model(model_name="ManagedObject",db_table="sa_managedobject",db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("ip_ipv4address","mac",MACField("MAC",null=True,blank=True))
        db.add_column("ip_ipv4address","managed_object",models.ForeignKey(ManagedObject,null=True,blank=True))
        db.add_column("ip_ipv4address","auto_update_mac",models.BooleanField("Auto Update MAC",default=False))
    
    def backwards(self):
        db.drop_column("ip_ipv4address","managed_object_id")
        db.drop_column("ip_ipv4address","mac")
        db.drop_column("ip_ipv4address","auto_update_mac")