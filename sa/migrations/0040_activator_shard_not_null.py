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
    def forwards(self):
        db.execute("ALTER TABLE sa_activator ALTER shard_id SET NOT NULL")
<<<<<<< HEAD

    def backwards(self):
        pass

=======
    
    def backwards(self):
        pass
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
