# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Make peer.asn_id nullable
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        rows = db.execute("SELECT id FROM peer_as WHERE asn = 0")
        as_id = rows[0][0]
        db.execute("ALTER TABLE ip_prefix ALTER asn_id DROP NOT NULL")
        db.execute("""
            UPDATE ip_prefix
            SET asn_id = NULL
            WHERE asn_id = %s
        """, [as_id])

    def backwards(self):
        pass
