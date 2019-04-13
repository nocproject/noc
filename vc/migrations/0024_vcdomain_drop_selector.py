# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vcdomain drop selector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    depends_on = [("sa", "0072_managedobject_set_vcdomain")]

    def forwards(self):
        db.drop_column("vc_vcdomain", "selector_id")

    def backwards(self):
        pass
