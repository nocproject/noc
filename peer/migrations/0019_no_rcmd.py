# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        db.delete_column("peer_peeringpoint","lg_rcmd")
        db.delete_column("peer_peeringpoint","provision_rcmd")
    
    def backwards(self):
        "Write your backwards migration here"
