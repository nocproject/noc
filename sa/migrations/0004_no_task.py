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
    
    def forwards(self):
        db.delete_table('sa_task')
        
    def backwards(self):
        
        # Model 'Task'
        db.create_table('sa_task', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('task_id', models.IntegerField("Task",unique=True)),
            ('start_time', models.DateTimeField("Start Time",auto_now_add=True)),
            ('end_time', models.DateTimeField("End Time")),
            ('profile_name', models.CharField("Profile",max_length=64)),
            ('stream_url', models.CharField("Stream URL",max_length=128)),
            ('action', models.CharField("Action",max_length=64)),
            ('args', models.TextField("Args")),
            ('status', models.CharField("Status",max_length=1,choices=[("n","New"),("p","In Progress"),("f","Failure"),("c","Complete")])),
            ('out', models.TextField("Out"))
        ))
        
        db.send_create_signal('sa', ['Task'])
