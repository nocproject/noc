# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("UPDATE sa_managedobject SET name=%s,profile_name=%s WHERE name=%s",["SAE","NOC.SAE","ROOT"])

=======
    
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET name=%s,profile_name=%s WHERE name=%s",["SAE","NOC.SAE","ROOT"])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.execute("UPDATE sa_managedobject SET name=%s,profile_name=%s WHERE name=%s",["ROOT","NOC","SAE"])
