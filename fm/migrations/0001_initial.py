# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'MIB'
        db.create_table('fm_mib', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.TextField("Description",blank=True,null=True)),
            ('last_updated', models.DateTimeField("Last Updated")),
            ('uploaded', models.DateTimeField("Uploaded"))
        ))
        
        # Mock Models
        MIB = db.mock_model(model_name='MIB', db_table='fm_mib', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'MIBData'
        db.create_table('fm_mibdata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mib', models.ForeignKey(MIB,verbose_name=MIB)),
            ('oid', models.CharField("OID",max_length=128,unique=True)),
            ('name', models.CharField("Name",max_length=128,unique=True)),
            ('description', models.TextField("Description",blank=True,null=True))
        ))
        
        db.send_create_signal('fm', ['MIB','MIBData'])
    
    def backwards(self):
        db.delete_table('fm_mibdata')
        db.delete_table('fm_mib')
        
