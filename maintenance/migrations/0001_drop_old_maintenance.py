# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Drop old maintenance
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        lc = db.list_collection_names()
        # Drop maintenance
        if "noc.maintenancetype" in lc:
            db.drop_collection("noc.maintainancetype")
        if "noc.maintenance" in lc:
            db.drop_collection("noc.maintainance")
