# -*- coding: utf-8 -*-
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
        db.add_column("sa_managedobject","snmp_ro",models.CharField("RO Community",blank=True,null=True,max_length=64))
        db.add_column("sa_managedobject","snmp_rw",models.CharField("RW Community",blank=True,null=True,max_length=64))
    
    def backwards(self):
        db.delete_column("sa_managedobject","snmp_ro")
        db.delete_column("sa_managedobject","snmp_rw")
