# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.dns.models import *

class Migration:
    def forwards(self):
        db.rename_column("dns_dnszonerecordtype", "is_visible", "is_active")
    
    def backwards(self):
        db.rename_column("dns_dnszonerecordtype", "is_active", "is_visible")

