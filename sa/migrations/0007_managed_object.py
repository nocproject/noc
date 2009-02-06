# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *

class Migration:
    depends_on=(
        ("cm","0010_trap_source_ip"),
    )
    def forwards(self):
        
        # Model 'AdministrativeDomain'
        db.create_table('sa_administrativedomain', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('description', models.TextField("Description",null=True,blank=True))
        ))
        # Model 'ObjectGroup'
        db.create_table('sa_objectgroup', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('description', models.TextField("Description",null=True,blank=True))
        ))
        
        # Mock Models
        AdministrativeDomain = db.mock_model(model_name='AdministrativeDomain', db_table='sa_administrativedomain', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Activator = db.mock_model(model_name='Activator', db_table='sa_activator', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'ManagedObject'
        db.create_table('sa_managedobject', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('is_managed', models.BooleanField("Is Managed?",default=True)),
            ('administrative_domain', models.ForeignKey(AdministrativeDomain,verbose_name=AdministrativeDomain)),
            ('activator', models.ForeignKey(Activator,verbose_name=Activator)),
            ('profile_name', models.CharField("Profile",max_length=128,choices=profile_registry.choices)),
            ('scheme', models.IntegerField("Scheme",choices=[(TELNET,"telnet"),(SSH,"ssh"),(HTTP,"http")])),
            ('address', models.CharField("Address",max_length=64)),
            ('port', models.PositiveIntegerField("Port",blank=True,null=True)),
            ('user', models.CharField("User",max_length=32,blank=True,null=True)),
            ('password', models.CharField("Password",max_length=32,blank=True,null=True)),
            ('super_password', models.CharField("Super Password",max_length=32,blank=True,null=True)),
            ('remote_path', models.CharField("Path",max_length=32,blank=True,null=True)),
            ('trap_source_ip', models.IPAddressField("Trap Source IP",null=True)),
            ('trap_community', models.CharField("Trap Community",blank=True,null=True,max_length=64)),
            ('is_configuration_managed', models.BooleanField("Is Configuration Managed?",default=True)),
            ('repo_path', models.CharField("Repo Path",max_length=128,blank=True,null=True))
        ))
        # Mock Models
        ManagedObject = db.mock_model(model_name='ManagedObject', db_table='sa_managedobject', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectGroup = db.mock_model(model_name='ObjectGroup', db_table='sa_objectgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'ManagedObject.groups'
        db.create_table('sa_managedobject_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('managedobject', models.ForeignKey(ManagedObject, null=False)),
            ('objectgroup', models.ForeignKey(ObjectGroup, null=False))
        )) 
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        AdministrativeDomain = db.mock_model(model_name='AdministrativeDomain', db_table='sa_administrativedomain', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectGroup = db.mock_model(model_name='ObjectGroup', db_table='sa_objectgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'UserAccess'
        db.create_table('sa_useraccess', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(User,verbose_name=User)),
            ('administrative_domain', models.ForeignKey(AdministrativeDomain,verbose_name="Administrative Domain",blank=True,null=True)),
            ('group', models.ForeignKey(ObjectGroup,verbose_name="Group",blank=True,null=True)),
        ))
        
        db.send_create_signal('sa', ['AdministrativeDomain','ObjectGroup','ManagedObject','UserAccess'])
    
    def backwards(self):
        db.delete_table('sa_managedobject_groups')
        db.delete_table('sa_useraccess')
        db.delete_table('sa_managedobject')
        db.delete_table('sa_objectgroup')
        db.delete_table('sa_administrativedomain')
