# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_managedobject", "location",
            models.CharField("Location", max_length=256, null=True,
                blank=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "location")
