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
    depends_on=[
        ("main", "0035_prefix_table"),
    ]
    def forwards(self):
        db.add_column("sa_commandsnippet", "require_confirmation",
            models.BooleanField("Require Confirmation",
                    default=False))
<<<<<<< HEAD

    def backwards(self):
        db.delete_column("sa_commandsnippet", "require_confirmation")

=======
    
    def backwards(self):
        db.delete_column("sa_commandsnippet", "require_confirmation")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
