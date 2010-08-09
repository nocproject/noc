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
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.add_column("main_pyrule","is_builtin",models.BooleanField("Is Builtin",default=False))
    
    def backwards(self):
        db.delete_column("main_pyrule","is_builtin")
