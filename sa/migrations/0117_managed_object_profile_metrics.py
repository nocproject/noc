# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
# NOC modules
from noc.core.model.fields import PickledField


class Migration(object):
    def forwards(self):
        db.add_column("sa_managedobjectprofile", "metrics", PickledField(null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "metrics")
