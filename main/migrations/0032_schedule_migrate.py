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
    def forwards(self):
        # Create Any time pattern if not exists
        if db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s", ["Any"])[0][0]==0:
            db.execute("INSERT INTO main_timepattern(name, description) values(%s,%s)", ["Any","Always match"])
        time_pattern_id = db.execute("SELECT id FROM main_timepattern WHERE name=%s", ["Any"])[0][0]
        for pn, e, t in db.execute("SELECT periodic_name, is_enabled, run_every FROM sa_taskschedule"):
            db.execute("INSERT INTO main_schedule(periodic_name, is_enabled, time_pattern_id, run_every) VALUES(%s, %s, %s, %s )",
                [pn, e, time_pattern_id, t])
    
    def backwards(self):
        pass
    
