# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# PyRule.handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
=======
##----------------------------------------------------------------------
## PyRule.handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "main_pyrule", "handler",
            models.CharField("Handler", max_length=255,
                               null=True, blank=True))
        db.drop_column("main_pyrule", "is_builtin")
        db.execute("ALTER TABLE main_pyrule ALTER \"text\" DROP NOT NULL")

    def backwards(self):
        pass
