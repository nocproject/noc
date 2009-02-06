# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.cm.models import *

class Migration:
    depends_on=(
        ("sa","0005_activator"),
    )
    def forwards(self):
        Activator = db.mock_model(model_name='Activator', db_table='sa_activator', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Config'
        db.create_table('cm_config', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repo_path', models.CharField("Repo Path",max_length=128,unique=True)),
            ('push_every', models.PositiveIntegerField("Push Every (secs)",default=86400,blank=True,null=True)),
            ('next_push', models.DateTimeField("Next Push",blank=True,null=True)),
            ('last_push', models.DateTimeField("Last Push",blank=True,null=True)),
            ('pull_every', models.PositiveIntegerField("Pull Every (secs)",default=86400,blank=True,null=True)),
            ('next_pull', models.DateTimeField("Next Pull",blank=True,null=True)),
            ('last_pull', models.DateTimeField("Last Pull",blank=True,null=True)),
            ('activator',models.ForeignKey(Activator,verbose_name="Activator")),
            ('profile_name', models.CharField("Profile",max_length=128,choices=profile_registry.choices)),
            ('scheme', models.IntegerField("Scheme",choices=[(0,"telnet"),(1,"ssh")])),
            ('address', models.CharField("Address",max_length=64)),
            ('port', models.PositiveIntegerField("Port",blank=True,null=True)),
            ('user', models.CharField("User",max_length=32,blank=True,null=True)),
            ('password', models.CharField("Password",max_length=32,blank=True,null=True)),
            ('super_password', models.CharField("Super Password",max_length=32,blank=True,null=True)),
            ('remote_path', models.CharField("Path",max_length=32,blank=True,null=True))
        ))
        # Mock Models
        Config = db.mock_model(model_name='Config', db_table='cm_config', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectCategory = db.mock_model(model_name='ObjectCategory', db_table='cm_objectcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'Config.categories'
        db.create_table('cm_config_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('config', models.ForeignKey(Config, null=False)),
            ('objectcategory', models.ForeignKey(ObjectCategory, null=False))
        )) 
        # Model 'PrefixList'
        db.create_table('cm_prefixlist', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repo_path', models.CharField("Repo Path",max_length=128,unique=True)),
            ('push_every', models.PositiveIntegerField("Push Every (secs)",default=86400,blank=True,null=True)),
            ('next_push', models.DateTimeField("Next Push",blank=True,null=True)),
            ('last_push', models.DateTimeField("Last Push",blank=True,null=True)),
            ('pull_every', models.PositiveIntegerField("Pull Every (secs)",default=86400,blank=True,null=True)),
            ('next_pull', models.DateTimeField("Next Pull",blank=True,null=True)),
            ('last_pull', models.DateTimeField("Last Pull",blank=True,null=True))
        ))
        # Mock Models
        PrefixList = db.mock_model(model_name='PrefixList', db_table='cm_prefixlist', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectCategory = db.mock_model(model_name='ObjectCategory', db_table='cm_objectcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'PrefixList.categories'
        db.create_table('cm_prefixlist_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('prefixlist', models.ForeignKey(PrefixList, null=False)),
            ('objectcategory', models.ForeignKey(ObjectCategory, null=False))
        )) 
        # Model 'DNS'
        db.create_table('cm_dns', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repo_path', models.CharField("Repo Path",max_length=128,unique=True)),
            ('push_every', models.PositiveIntegerField("Push Every (secs)",default=86400,blank=True,null=True)),
            ('next_push', models.DateTimeField("Next Push",blank=True,null=True)),
            ('last_push', models.DateTimeField("Last Push",blank=True,null=True)),
            ('pull_every', models.PositiveIntegerField("Pull Every (secs)",default=86400,blank=True,null=True)),
            ('next_pull', models.DateTimeField("Next Pull",blank=True,null=True)),
            ('last_pull', models.DateTimeField("Last Pull",blank=True,null=True))
        ))
        # Mock Models
        DNS = db.mock_model(model_name='DNS', db_table='cm_dns', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectCategory = db.mock_model(model_name='ObjectCategory', db_table='cm_objectcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'DNS.categories'
        db.create_table('cm_dns_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dns', models.ForeignKey(DNS, null=False)),
            ('objectcategory', models.ForeignKey(ObjectCategory, null=False))
        )) 
        
        db.send_create_signal('cm', ['Config','PrefixList','DNS'])
    
    def backwards(self):
        db.delete_table('cm_config_categories')
        db.delete_table('cm_prefixlist_categories')
        db.delete_table('cm_dns_categories')
        
        db.delete_table('cm_dns')
        db.delete_table('cm_prefixlist')
        db.delete_table('cm_config')
