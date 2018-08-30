# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Set VRF.rd to nullable/non-unique
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute("ALTER TABLE ip_vrf DROP CONSTRAINT \"ip_vrf_rd_key\"")
        db.execute("ALTER TABLE ip_vrf ALTER COLUMN rd DROP NOT NULL")

    def backwards(self):
        pass
