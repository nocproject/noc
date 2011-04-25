# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db

class Migration:
    NAME = "default"
    def forwards(self):
        shard_id = db.execute("SELECT id FROM main_shard WHERE name=%s", [self.NAME])[0][0]
        db.execute("UPDATE sa_activator SET shard_id=%s", [shard_id])
    
    def backwards(self):
        pass
    
