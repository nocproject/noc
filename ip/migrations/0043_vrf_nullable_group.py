# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Make VRF.vrf_group nullable
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute("ALTER TABLE ip_vrf ALTER vrf_group_id DROP NOT NULL")

    def backwards(self):
        pass
