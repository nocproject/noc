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
        
        # Model 'TaskSchedule'
        db.create_table('sa_taskschedule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('periodic_name', models.CharField("Periodic Task",max_length=64,choices=periodic_registry.choices)),
            ('is_enabled', models.BooleanField("Enabled?",default=False)),
            ('run_every', models.PositiveIntegerField("Run Every (secs)",default=86400)),
            ('retries', models.PositiveIntegerField("Retries",default=1)),
            ('retry_delay', models.PositiveIntegerField("Retry Delay (secs)",default=60)),
            ('timeout', models.PositiveIntegerField("Timeout (secs)",default=300)),
            ('next_run', models.DateTimeField("Next Run",auto_now_add=True)),
            ('retries_left', models.PositiveIntegerField("Retries Left",default=1))
        ))
        
        db.send_create_signal('sa', ['TaskSchedule'])
    
    def backwards(self):
        db.delete_table('sa_taskschedule')
        
