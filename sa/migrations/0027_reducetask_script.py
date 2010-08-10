# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##
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
        db.execute("DELETE FROM sa_maptask")
        db.execute("DELETE FROM sa_reducetask")
        db.execute("COMMIT")
        db.add_column("sa_reducetask","script",models.TextField("Script"))
        db.delete_column("sa_reducetask","reduce_script")
    
    def backwards(self):
        db.execute("DELETE FROM sa_maptask")
        db.execute("DELETE FROM sa_reducetask")
        db.execute("COMMIT")
        db.delete_column("sa_reducetask","script")
        db.add_column("sa_reducetask","reduce_script",models.CharField("Script",maxlength=256))
