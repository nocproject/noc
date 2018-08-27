# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Remove _legacy_id from resource group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    depends_on = [
        ("phone", "0002_migrate_termination_groups")
    ]

    def forwards(self):
        db = get_db()
        coll = db["resourcegroups"]
        coll.update_many({
            "_legacy_id": {
                "$exists": True
            }
        }, {
            "$unset": {
                "_legacy_id": ""
            }
        })

    def backwards(self):
        pass
