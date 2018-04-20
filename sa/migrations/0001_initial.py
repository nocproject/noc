# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:

    def forwards(self):

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

    def backwards(self):
        db.delete_table('sa_task')

