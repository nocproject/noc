# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from south.db import db
from django.db import models
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from south.db import db
from noc.main.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    def forwards(self):
        db.add_column("main_userprofile", "theme",
                      models.CharField("Theme", max_length=32,
                                       null=True, blank=True))

    def backwards(self):
        db.delete_column("main_userprofile", "theme")
