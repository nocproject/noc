# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.cm.models import *

OBJECT_TYPES=["config","dns","prefixlist","rpsl"]
OBJECT_TYPE_CHOICES=[(x,x) for x in OBJECT_TYPES]

class Migration:
    
    def forwards(self):
        db.delete_column("cm_objectcategory","notify_immediately")
        db.delete_column("cm_objectcategory","notify_delayed")
        
        db.create_table('cm_objectlocation', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.CharField("Description",max_length=128,null=True,blank=True))
        ))
        
        ObjectLocation = db.mock_model(model_name='ObjectLocation', db_table='cm_objectlocation', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        db.execute("INSERT INTO cm_objectlocation(name,description) values(%s,%s)",["default","default location"])
        loc_id=db.execute("SELECT id FROM cm_objectlocation WHERE name=%s",["default"])[0][0]
        
        for ot in OBJECT_TYPES:
            db.add_column("cm_%s"%ot,"location",models.ForeignKey(ObjectLocation,null=True,blank=True))
            db.execute("UPDATE cm_%s SET location_id=%%s"%ot,[loc_id])
            db.execute("ALTER TABLE cm_%s ALTER location_id SET NOT NULL"%ot)
        
        # Mock Models
        ObjectCategory = db.mock_model(model_name='ObjectCategory', db_table='cm_objectcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectLocation = db.mock_model(model_name='ObjectLocation', db_table='cm_objectlocation', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'ObjectAccess'
        db.create_table('cm_objectaccess', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('type', models.CharField("Type",max_length=16,choices=OBJECT_TYPE_CHOICES)),
            ('category', models.ForeignKey(ObjectCategory,verbose_name="Category",blank=True,null=True)),
            ('location', models.ForeignKey(ObjectLocation,verbose_name="Location",blank=True,null=True)),
            ('user', models.ForeignKey(User,verbose_name=User))
        ))
        
        # Mock Models
        ObjectCategory = db.mock_model(model_name='ObjectCategory', db_table='cm_objectcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectLocation = db.mock_model(model_name='ObjectLocation', db_table='cm_objectlocation', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'ObjectNotify'
        db.create_table('cm_objectnotify', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('type', models.CharField("Type",max_length=16,choices=OBJECT_TYPE_CHOICES)),
            ('category', models.ForeignKey(ObjectCategory,verbose_name="Category",blank=True,null=True)),
            ('location', models.ForeignKey(ObjectLocation,verbose_name="Location",blank=True,null=True)),
            ('emails', models.CharField("Emails",max_length=128)),
            ('notify_immediately', models.BooleanField("Notify Immediately")),
            ('notify_delayed', models.BooleanField("Notify Delayed")),
        ))
        
        db.send_create_signal('cm', ['ObjectLocation','ObjectAccess','ObjectNotify'])
    
    def backwards(self):
        for ot in OBJECT_TYPES:
            db.delete_column("cm_%s"%ot,"location_id")
        db.delete_table('cm_objectnotify')
        db.delete_table('cm_objectaccess')
        db.add_column("cm_objectcategory","notify_immediately",models.TextField("Notify Immediately",blank=True,null=True))
        db.add_column("cm_objectcategory","notify_delayed",models.TextField("Notify Delayed",blank=True,null=True))
        db.delete_table('cm_objectlocation')
        
