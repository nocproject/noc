# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
from south.db import db

class Migration:
    NAME = "default"
    def forwards(self):
        shard_id = db.execute("SELECT id FROM main_shard WHERE name=%s", [self.NAME])[0][0]
        db.execute("UPDATE sa_activator SET shard_id=%s", [shard_id])
<<<<<<< HEAD

    def backwards(self):
        pass

=======
    
    def backwards(self):
        pass
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
