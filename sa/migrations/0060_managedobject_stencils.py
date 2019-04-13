# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile stencils
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile", "shape", models.CharField("Shape", blank=True, null=True, max_length=128)
        )
        db.add_column("sa_managedobject", "shape", models.CharField("Shape", blank=True, null=True, max_length=128))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "shape")
        db.delete_column("sa_managedobject", "shape")
