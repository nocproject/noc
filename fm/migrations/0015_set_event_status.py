# ----------------------------------------------------------------------
# set event status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute("UPDATE fm_event SET status='U' WHERE subject IS NULL")
        self.db.execute(
            """UPDATE fm_event SET status='C' WHERE subject IS NOT NULL
               AND \"timestamp\"<('now'::timestamp-'1day'::interval)"""
        )
        self.db.execute(
            """UPDATE fm_event SET status='A' WHERE subject IS NOT NULL
               AND \"timestamp\">=('now'::timestamp-'1day'::interval)"""
        )
