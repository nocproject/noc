# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Set .state NOT NULL
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        # Get default resource state id
        r = db.execute("SELECT id FROM main_resourcestate WHERE is_default = true")
        if len(r) != 1:
            raise Exception("Cannot get default state")
        ds = r[0][0]
        # Set up default state
        db.execute("UPDATE ip_vrf SET state_id = %s", [ds])
        db.execute("UPDATE ip_prefix SET state_id = %s", [ds])
        db.execute("UPDATE ip_address SET state_id = %s", [ds])

    def backwards(self):
        pass
