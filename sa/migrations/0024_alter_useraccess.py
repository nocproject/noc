# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("ALTER TABLE sa_useraccess ALTER selector_id SET NOT NULL")


=======
    
    def forwards(self):
        db.execute("ALTER TABLE sa_useraccess ALTER selector_id SET NOT NULL")
    
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        """Write your backwards migration here"""
