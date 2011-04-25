# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db

class Migration:
    def forwards(self):
        db.execute("ALTER TABLE sa_activator ALTER shard_id SET NOT NULL")
    
    def backwards(self):
        pass
    
