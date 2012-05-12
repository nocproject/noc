# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Add .is_hidden field to CustomField
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from south.db import db
from noc.main.models import *

class Migration:
    def forwards(self):
        db.add_column("main_customfield", "is_hidden",
            models.BooleanField("Is Hidden", default=False))

    def backwards(self):
        db.delete_column("main_customfield", "is_hidden")
