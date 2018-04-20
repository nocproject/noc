# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
##
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
from south.db import db
from django.db import models

<<<<<<< HEAD

class Migration:

=======
class Migration:
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        db.execute("DELETE FROM sa_maptask")
        db.execute("DELETE FROM sa_reducetask")
        db.execute("COMMIT")
<<<<<<< HEAD
        db.add_column("sa_reducetask", "script", models.TextField("Script"))
        db.delete_column("sa_reducetask", "reduce_script")

=======
        db.add_column("sa_reducetask","script",models.TextField("Script"))
        db.delete_column("sa_reducetask","reduce_script")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.execute("DELETE FROM sa_maptask")
        db.execute("DELETE FROM sa_reducetask")
        db.execute("COMMIT")
<<<<<<< HEAD
        db.delete_column("sa_reducetask", "script")
        db.add_column("sa_reducetask", "reduce_script", models.CharField("Script", maxlength=256))
=======
        db.delete_column("sa_reducetask","script")
        db.add_column("sa_reducetask","reduce_script",models.CharField("Script",maxlength=256))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
