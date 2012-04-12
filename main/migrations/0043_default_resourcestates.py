# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Default ResourceState
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        # ResourceState
        db.execute("""
            INSERT INTO main_resourcestate(id, name, description,
                is_active, is_starting, is_default, is_provisioned, step_to_id)
            VALUES
                (1, 'ALLOCATED', 'Permanently allocated resource', true,
                    true, true, true, NULL),
                (2, 'EXPIRED', 'Allocation expired', true,
                    false, false, true, NULL),
                (3, 'PLANNED', 'Planned to allocate', true,
                    true, false, false, NULL),
                (4, 'RESERVED', 'Temporary reserved', true,
                    true, false, false, 2),
                (5, 'SUSPEND', 'Temporary out of service', true,
                    false, false, false, NULL)

        """)
        db.execute("SELECT setval('main_resourcestate_id_seq'::regclass, 5)")

    def backwards(self):
        pass
