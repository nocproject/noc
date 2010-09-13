# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.main.models import *

class Migration:
    depends_on=(
        ("sa","0003_task_schedule"),
    )
    def forwards(self):
        db.execute("UPDATE sa_taskschedule SET periodic_name='main.cleanup' WHERE periodic_name='main.cleanup_sessions'")

    def backwards(self):
        db.execute("UPDATE sa_taskschedule SET periodic_name='main.cleanup_sessions' WHERE periodic_name='main.cleanup'")
