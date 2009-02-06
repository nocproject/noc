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
        db.delete_column("dns_dnszoneprofile","zone_transfer_acl")
    
    def backwards(self):
        db.add_column("dns_dnszoneprofile","zone_transfer_acl",models.CharField("named zone transfer ACL",max_length=64,default="acl-transfer"))
