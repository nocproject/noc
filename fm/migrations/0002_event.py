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
        
        # Model 'EventPriority'
        db.create_table('fm_eventpriority', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('priority', models.IntegerField("Priority")),
            ('description', models.TextField("Description",blank=True,null=True))
        ))
        # Model 'EventCategory'
        db.create_table('fm_eventcategory', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('description', models.TextField("Description",blank=True,null=True))
        ))
        # Mock Models
        EventPriority = db.mock_model(model_name='EventPriority', db_table='fm_eventpriority', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        EventCategory = db.mock_model(model_name='EventCategory', db_table='fm_eventcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventClass'
        db.create_table('fm_eventclass', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64)),
            ('category', models.ForeignKey(EventCategory,verbose_name="Event Category")),
            ('default_priority', models.ForeignKey(EventPriority,verbose_name="Default Priority")),
            ('variables', models.CharField("Variables",max_length=128,blank=True,null=True)),
            ('subject_template', models.CharField("Subject Template",max_length=128)),
            ('body_template', models.TextField("Body Template")),
            ('last_modified', models.DateTimeField("last_modified",auto_now=True))
        ))
        # Mock Models
        EventClass = db.mock_model(model_name='EventClass', db_table='fm_eventclass', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventClassificationRule'
        db.create_table('fm_eventclassificationrule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event_class', models.ForeignKey(EventClass,verbose_name="Event Class")),
            ('name', models.CharField("Name",max_length=64)),
            ('preference', models.IntegerField("Preference",1000))
        ))
        
        # Mock Models
        EventClassificationRule = db.mock_model(model_name='EventClassificationRule', db_table='fm_eventclassificationrule', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventClassificationRE'
        db.create_table('fm_eventclassificationre', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rule', models.ForeignKey(EventClassificationRule,verbose_name="Event Classification Rule")),
            ('left_re', models.CharField("Left RE",max_length=256)),
            ('right_re', models.CharField("Right RE",max_length=256))
        ))
        
        # Mock Models
        ManagedObject = db.mock_model(model_name='ManagedObject', db_table='sa_managedobject', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Event = db.mock_model(model_name='Event', db_table='fm_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Event'
        db.create_table('fm_event', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timestamp', models.DateTimeField("Timestamp")),
            ('managed_object', models.ForeignKey(ManagedObject,verbose_name="Managed Object")),
            ('event_priority', models.ForeignKey(EventPriority,verbose_name="Priority")),
            ('event_category', models.ForeignKey(EventCategory,verbose_name="Event Class")),
            ('event_class', models.ForeignKey(EventClass,verbose_name="Event Class")),
            ('parent', models.ForeignKey(Event,verbose_name="Parent",blank=True,null=True)),
            ('subject', models.CharField("Subject",max_length=256,null=True,blank=True)),
            ('body', models.TextField("Body",null=True,blank=True))
        ))
        
        # Mock Models
        Event = db.mock_model(model_name='Event', db_table='fm_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventData'
        db.create_table('fm_eventdata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(Event,verbose_name=Event)),
            ('key', models.CharField("Key",max_length=64)),
            ('value', models.TextField("Value",blank=True,null=True)),
            ('type', models.CharField("Type",max_length=1,choices=[(">","Received"),("V","Variable"),("R","Resolved")],default=">"))
        ))
        db.create_index('fm_eventdata', ['event_id','key','type'], unique=True, db_tablespace='')
        
        db.send_create_signal('fm', ['EventPriority','EventCategory','EventClass','EventClassificationRule','EventClassificationRE',
            'Event','EventData'])
    
    def backwards(self):
        db.delete_table('fm_eventdata')
        db.delete_table('fm_event')
        db.delete_table('fm_eventclassificationre')
        db.delete_table('fm_eventclassificationrule')
        db.delete_table('fm_eventclass')
        db.delete_table('fm_eventcategory')
        db.delete_table('fm_eventpriority')
