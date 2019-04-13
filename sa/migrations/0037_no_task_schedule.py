# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# no task schedule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    depends_on = [
        ("main", "0032_schedule_migrate"),
    ]

    def forwards(self):
        db.delete_table("sa_taskschedule")

    def backwards(self):
        pass
