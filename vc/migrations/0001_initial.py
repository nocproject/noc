# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Initial migration for VC application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.vc.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'VCDomain'
        db.create_table('vc_vcdomain', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.TextField("Description",blank=True,null=True))
        ))
        
        # Mock Models
        VCDomain = db.mock_model(model_name='VCDomain', db_table='vc_vcdomain', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'VC'
        db.create_table('vc_vc', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vc_domain', models.ForeignKey(VCDomain,verbose_name="VC Domain")),
            ('type', models.CharField("Type",max_length=1)),
            ('l1', models.IntegerField("Label 1")),
            ('l2', models.IntegerField("Label 2",default=0)),
            ('description', models.CharField("Description",max_length=256))
        ))
        db.create_index('vc_vc', ['vc_domain_id','type','l1','l2'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('vc', ['VCDomain','VC'])
    
    def backwards(self):
        db.delete_table('vc_vc')
        db.delete_table('vc_vcdomain')
        
