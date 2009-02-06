# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.ip.models import *

class Migration:
    depends_on=(
        ("peer" ,"0001_initial"),
    )
    
    def forwards(self):
        
        # Model 'VRFGroup'
        db.create_table('ip_vrfgroup', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("VRF Group",unique=True,max_length=64)),
            ('unique_addresses', models.BooleanField("Unique addresses in group"))
        ))
        
        # Mock Models
        VRFGroup = db.mock_model(model_name='VRFGroup', db_table='ip_vrfgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'VRF'
        db.create_table('ip_vrf', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("VRF name",unique=True,max_length=64)),
            ('vrf_group', models.ForeignKey(VRFGroup,verbose_name="VRF Group")),
            ('rd', models.CharField("rd",unique=True,max_length=21)),
            ('tt', models.IntegerField("TT",blank=True,null=True))
        ))
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        VRF = db.mock_model(model_name='VRF', db_table='ip_vrf', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'IPv4BlockAccess'
        db.create_table('ip_ipv4blockaccess', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(User,verbose_name=User)),
            ('vrf', models.ForeignKey(VRF,verbose_name=VRF)),
            ('prefix', models.CharField("prefix",max_length=18)),
            ('tt', models.IntegerField("TT",blank=True,null=True))
        ))
        db.create_index('ip_ipv4blockaccess', ['user_id','vrf_id','prefix'], unique=True, db_tablespace='')
        
        
        # Mock Models
        VRF = db.mock_model(model_name='VRF', db_table='ip_vrf', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        AS = db.mock_model(model_name='AS', db_table='peer_as', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'IPv4Block'
        db.create_table('ip_ipv4block', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('description', models.CharField("Description",max_length=64)),
            ('prefix', models.CharField("prefix",max_length=18)),
            ('vrf', models.ForeignKey(VRF)),
            ('asn', models.ForeignKey(AS)),
            ('modified_by', models.ForeignKey(User,verbose_name=User)),
            ('last_modified', models.DateTimeField("Last modified",auto_now=True,auto_now_add=True)),
            ('tt', models.IntegerField("TT",blank=True,null=True))
        ))
        db.create_index('ip_ipv4block', ['prefix','vrf_id'], unique=True, db_tablespace='')
        
        
        # Mock Models
        VRF = db.mock_model(model_name='VRF', db_table='ip_vrf', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'IPv4Address'
        db.create_table('ip_ipv4address', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vrf', models.ForeignKey(VRF,verbose_name=VRF)),
            ('fqdn', models.CharField("FQDN",max_length=64)),
            ('ip', models.IPAddressField("IP")),
            ('description', models.CharField("Description",blank=True,null=True,max_length=64)),
            ('modified_by', models.ForeignKey(User,verbose_name=User)),
            ('last_modified', models.DateTimeField("Last modified",auto_now=True,auto_now_add=True)),
            ('tt', models.IntegerField("TT",blank=True,null=True))
        ))
        db.create_index('ip_ipv4address', ['vrf_id','ip'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('ip', ['VRFGroup','VRF','IPv4BlockAccess','IPv4Block','IPv4Address'])
    
    def backwards(self):
        db.delete_table('ip_ipv4address')
        db.delete_table('ip_ipv4block')
        db.delete_table('ip_ipv4blockaccess')
        db.delete_table('ip_vrf')
        db.delete_table('ip_vrfgroup')
        
