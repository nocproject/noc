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
    depends_on=[
        ("sa", "0003_task_schedule"),
    ]
    def forwards(self):
        # TimePattern
        TimePattern = db.mock_model(model_name="TimePattern",
            db_table="main_timepattern", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        # Model "TaskSchedule"
        db.create_table("main_schedule", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("periodic_name", models.CharField("Periodic Task", max_length=64)),
            ("is_enabled", models.BooleanField("Enabled?", default=False)),
            ("time_pattern", models.ForeignKey(TimePattern,
                                             verbose_name="Time Pattern")),
            ("run_every", models.PositiveIntegerField("Run Every (secs)",default=86400)),
            ("timeout", models.PositiveIntegerField("Timeout (secs)",null=True, blank=True)),
            ("last_run", models.DateTimeField("Last Run", blank=True, null=True)),
            ("last_status", models.BooleanField("Last Status", default=True))
        ))
        db.send_create_signal("main", ["Schedule"])
<<<<<<< HEAD

    def backwards(self):
        db.delete_table("main_schedule")

=======
    
    def backwards(self):
        db.delete_table("main_schedule")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
