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
        if db.execute("SELECT COUNT(*) FROM main_shard WHERE name=%s", [self.NAME])[0][0]==0:
            db.execute("INSERT INTO main_shard(name, is_active, description) VALUES(%s, %s, %s)",
                [self.NAME, True, "Default shard"])
        
    
    def backwards(self):
        pass
    
