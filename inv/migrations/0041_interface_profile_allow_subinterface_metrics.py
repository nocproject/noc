# ----------------------------------------------------------------------
# Rename InterfaceProfile.container to parent
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    def migrate(self):
        coll = self.mongo_db["noc.interface_profiles"]
        coll.update_many(
            {"allow_subinterface_metrics": True}, {"$set": {"subinterface_apply_policy": "I"}}
        )
