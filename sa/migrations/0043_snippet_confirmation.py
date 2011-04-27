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
    depends_on=[
        ("main", "0035_prefix_table"),
    ]
    def forwards(self):
        db.add_column("sa_commandsnippet", "require_confirmation",
            models.BooleanField("Require Confirmation",
                    default=False))
    
    def backwards(self):
        db.delete_column("sa_commandsnippet", "require_confirmation")
    
