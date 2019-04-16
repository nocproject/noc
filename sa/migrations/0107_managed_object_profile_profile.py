# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile enable_box_discovery_profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from django.db import models
from south.db import db


class Migration(object):
    def forwards(self):
        db.add_column("sa_managedobjectprofile", "enable_box_discovery_profile", models.BooleanField(default=True))

    def backwards(self):
        pass
