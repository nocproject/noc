# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.dns.models import *

class Migration:
    def forwards(self):
        db.add_column("dns_dnsserver","generator_name",models.CharField("Generator",max_length=32,default="BINDv9"))
        db.execute("UPDATE dns_dnsserver SET generator_name=%s",["BINDv9"])
    
    def backwards(self):
        raise "No backwards way"
