# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration:

    def forwards(self):
        db.delete_column("peer_peeringpoint", "lg_rcmd")
        db.delete_column("peer_peeringpoint", "provision_rcmd")

    def backwards(self):
        pass
