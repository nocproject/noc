# ----------------------------------------------------------------------
# change eventarchivationrule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.create_index("fm_eventarchivationrule", ["event_class_id", "action"], unique=True)
        try:
            self.db.create_index("fm_eventarchivationrule", ["event_class_id"], unique=True)
        except Exception:
            pass
