# ---------------------------------------------------------------------
# Create "default" interface profie
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

DEFAULT_NAME = "default"


class Migration(BaseMigration):
    def migrate(self):
        c = self.mongo_db.noc.interface_profiles
        if not c.count_documents({"name": DEFAULT_NAME}):
            c.insert_one(
                {
                    "name": DEFAULT_NAME,
                    "description": "Fallback interface profile.\nDo not remove or rename",
                    "link_events": "A",
                }
            )
