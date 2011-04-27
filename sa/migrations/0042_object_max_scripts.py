# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        db.add_column("sa_managedobject", "max_scripts",
                models.IntegerField("Max. Scripts", null=True, blank=True))
    
    def backwards(self):
        db.delete_column("sa_managedobject", "max_scripts")
