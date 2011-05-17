# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.main.models import *
from noc import settings

class Migration:
    def forwards(self):
        db.delete_column("main_userprofile", "preferred_language_id")
        db.add_column("main_userprofile", "preferred_language",
                      models.CharField("Preferred Language", max_length=16,
                                        null=True, blank=True))
    
    def backwards(self):
        pass    
