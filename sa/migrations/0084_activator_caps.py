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
from django.db import models

class Migration:
    def forwards(self):
        db.add_column(
            "sa_activator",
            "min_sessions",
            models.IntegerField(_("Min Sessions"), default=0)
        )
        db.add_column(
            "sa_activator",
            "min_members",
            models.IntegerField(_("Min Members"), default=0)
        )

    def backwards(self):
        db.delete_column("sa_activator", "min_sessions")
        db.delete_column("sa_activator", "min_members")
