# ----------------------------------------------------------------------
# Cleanup AlarmClass Severities to Labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.mongo_db["alarmrules"].delete_many(
            {"actions.severity": {"$exists": True}, "match.labels": {"$ne": []}},
        )
