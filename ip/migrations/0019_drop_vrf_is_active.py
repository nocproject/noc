# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Drop VRF.is_active
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.ip.models import *
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.drop_column("ip_vrf", "is_active")

    def backwards(self):
        db.create_column("ip_vrf", "is_active",
                         models.BooleanField(default=True))
