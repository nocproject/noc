# -*- coding: utf-8 -*-
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
        db.add_column("fm_eventpriority","font_color",models.CharField("Font Color",max_length=32,blank=True,null=True))
        db.add_column("fm_eventpriority","background_color",models.CharField("Background Color",max_length=32,blank=True,null=True))
    
    def backwards(self):
        db.delete_column("fm_eventpriority","font_color")
        db.delete_column("fm_eventpriority","background_color")
