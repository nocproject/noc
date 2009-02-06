# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'CommunityType'
        db.create_table('peer_communitytype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Description",max_length=32,unique=True))
        ))
        
        # Mock Models
        CommunityType = db.mock_model(model_name='CommunityType', db_table='peer_communitytype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Community'
        db.create_table('peer_community', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('community', models.CharField("Community",max_length=20,unique=True)),
            ('type', models.ForeignKey(CommunityType,verbose_name="Type")),
            ('description', models.CharField("Description",max_length=64))
        ))
        
        db.send_create_signal('peer', ['CommunityType','Community'])
    
    def backwards(self):
        db.delete_table('peer_community')
        db.delete_table('peer_communitytype')
        
