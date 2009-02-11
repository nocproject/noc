# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Create "default" VC domain, if not exists
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.vc.models import *

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM vc_vcdomain WHERE name=%s",["default"])[0][0]==0:
            db.execute("INSERT INTO vc_vcdomain(name,description) VALUES(%s,%s)",["default","Default VC Domain"])
    
    def backwards(self):
        "Write your backwards migration here"
