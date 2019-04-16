# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile clear_links
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
        db.add_column("sa_managedobjectprofile", "clear_links_on_platform_change", models.BooleanField(default=False))
        db.add_column("sa_managedobjectprofile", "clear_links_on_serial_change", models.BooleanField(default=False))

    def backwards(self):
        pass
