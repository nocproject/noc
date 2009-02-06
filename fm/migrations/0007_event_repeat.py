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
        
        # Model 'EventRepeat'
        db.create_table('fm_eventrepeat', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(Event,verbose_name="Event")),
            ('timestamp', models.DateTimeField("Timestamp"))
        ))
        # Mock Models
        EventClass = db.mock_model(model_name='EventClass', db_table='fm_eventclass', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventClassVar'
        db.create_table('fm_eventclassvar', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event_class', models.ForeignKey(EventClass,verbose_name="Event Class")),
            ('name', models.CharField("Name",max_length=64)),
            ('required', models.BooleanField("Required",default=True)),
            ('repeat_suppression', models.BooleanField("Repeat Suppression",default=False))
        ))
        db.create_index('fm_eventclassvar', ['event_class_id','name'], unique=True, db_tablespace='')
        db.send_create_signal('fm', ['EventRepeat','EventClassVar'])
        
        db.add_column('fm_eventclass','repeat_suppression',models.BooleanField("Repeat Suppression",default=False))
        db.add_column('fm_eventclass','repeat_suppression_interval',models.IntegerField("Repeat Suppression interval (secs)",default=3600))
        # Migrate variables
        for id,vars in db.execute("SELECT id,variables FROM fm_eventclass"):
            if vars:
                for v in [v.strip() for v in vars.split(",")]:
                    db.execute("INSERT INTO fm_eventclassvar(event_class_id,name,required,repeat_suppression) VALUES(%s,%s,true,false)",[id,v])
        db.delete_column('fm_eventclass','variables')        
    
    def backwards(self):
        db.delete_table('fm_eventrepeat')
        db.delete_column('fm_eventclass','repeat_suppression')
        db.delete_column('fm_eventclass','repeat_suppression_interval')
        db.delete_table('fm_eventclassvar')
        
