# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile nri
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
        db.add_column("sa_managedobjectprofile", "enable_box_discovery_nri", models.BooleanField(default=False))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_nri")
