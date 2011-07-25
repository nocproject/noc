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
        db.add_column("sa_commandsnippet", "permission_name",
                      models.CharField(_("Permission Name"), max_length=64,
                                       null=True, blank=True))
        db.add_column("sa_commandsnippet", "display_in_menu",
                      models.BooleanField(_("Show in menu"), default=False))
    
    def backwards(self):
        db.delete_column("sa_commandsnippet", "permission_name")
        db.delete_column("sa_commandsnippet", "display_in_menu")    
