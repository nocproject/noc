# ----------------------------------------------------------------------
# Optionally Organization and RIR on AS Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC module
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    def migrate(self):
        for col in ["organisation_id", "rir_id", "description"]:
            self.db.execute(f"ALTER TABLE peer_as ALTER {col} DROP NOT NULL")
        # Set Exists AS Profile set default
        self.mongo_db["asprofiles"].update_many({}, {"gen_rpsl": True, "validation_policy": "S"})
