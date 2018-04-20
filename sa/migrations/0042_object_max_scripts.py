# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
##
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
        db.add_column("sa_managedobject", "max_scripts",
                models.IntegerField("Max. Scripts", null=True, blank=True))

=======
    
    def forwards(self):
        db.add_column("sa_managedobject", "max_scripts",
                models.IntegerField("Max. Scripts", null=True, blank=True))
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_column("sa_managedobject", "max_scripts")
