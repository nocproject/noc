# ----------------------------------------------------------------------
# Migrate ActionCommand.disable_when_change
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.actioncommands"]
        coll.update_many(
            {"disable_when_change": {"$in": [True, False]}}, {"$unset": {"disable_when_change": ""}}
        )
