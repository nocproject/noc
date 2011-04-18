# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *

class Migration:
    depends_on=[
        ("main", "0032_schedule_migrate"),
    ]
    def forwards(self):
        db.delete_table("sa_taskschedule")
    
    def backwards(self):
        pass
