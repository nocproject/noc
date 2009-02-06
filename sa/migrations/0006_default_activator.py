# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM sa_activator")[0][0]==0:
            db.execute("INSERT INTO sa_activator(name,ip,is_active,auth) VALUES('default','127.0.0.1',true,'xxxxxxxxxxx')")
    
    def backwards(self):
        "Write your backwards migration here"
