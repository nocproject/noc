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

        # Model 'TaskSchedule'
        db.create_table('sa_taskschedule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('periodic_name', models.CharField("Periodic Task",max_length=64)),
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

