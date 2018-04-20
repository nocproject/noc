# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
import datetime
from south.db import db
<<<<<<< HEAD
from django.db import models
=======
from noc.fm.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_pyrule WHERE name=%s", ["refresh_config"])[0][0] == 0:
            db.execute("""INSERT INTO main_pyrule(name, interface, description, text, changed)
                       VALUES(%s, %s, %s, %s, %s)""",
                       ("refresh_config", "IEventTrigger", "stub", "@pyrule\ndef refresh_config(event):\n    pass",
                        datetime.datetime.now()))
        r_id = db.execute("SELECT id FROM main_pyrule WHERE name = %s", ["refresh_config"])[0][0]
        db.execute("""INSERT INTO fm_eventtrigger(name, is_enabled, event_class_re, pyrule_id)
                   VALUES(%s, %s, %s, %s)
                   """, ["Refresh Config", True, r"Config \| Config Changed", r_id])
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
