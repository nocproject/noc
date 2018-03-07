# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM peer_maintainer")[0][0] == 0:
            rir_id = db.execute("SELECT id FROM peer_rir LIMIT 1")[0][0]
            db.execute(
                "INSERT INTO peer_maintainer(maintainer,description,auth,rir_id) VALUES(%s,%s,%s,%s)",
                ["Default maintainer", "Please change to your maintainer", "NO AUTH", rir_id]
            )

    def backwards(self):
        pass
