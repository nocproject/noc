# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from south.db import db
from django.db import models
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.main.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    depends_on=(
        ("sa","0003_task_schedule"),
    )
    def forwards(self):
        db.execute("UPDATE sa_taskschedule SET periodic_name='main.cleanup' WHERE periodic_name='main.cleanup_sessions'")

    def backwards(self):
        db.execute("UPDATE sa_taskschedule SET periodic_name='main.cleanup_sessions' WHERE periodic_name='main.cleanup'")
