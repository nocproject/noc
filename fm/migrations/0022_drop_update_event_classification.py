# ----------------------------------------------------------------------
# drop update_event_classification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            "DROP FUNCTION update_event_classification(INTEGER,INTEGER,INTEGER,INTEGER,INTEGER,TEXT,TEXT,TEXT[][])"
        )
