# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party models
from south.db import db

NAMES = [
    "Other Normal",
    "Other Extended"
]


class Migration:

    def forwards(self):
        for n in NAMES:
            if db.execute("SELECT COUNT(*) FROM peer_communitytype WHERE name=%s", [n])[0][0] == 0:
                db.execute("INSERT INTO peer_communitytype(name) VALUES(%s)", [n])

    def backwards(self):
        pass
