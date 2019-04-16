# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cleanup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    depends_on = (("sa", "0003_task_schedule"),)

    def forwards(self):
        db.execute(
            "UPDATE sa_taskschedule SET periodic_name='main.cleanup' WHERE periodic_name='main.cleanup_sessions'"
        )

    def backwards(self):
        db.execute(
            "UPDATE sa_taskschedule SET periodic_name='main.cleanup_sessions' WHERE periodic_name='main.cleanup'"
        )
