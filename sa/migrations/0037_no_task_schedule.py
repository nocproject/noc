# ----------------------------------------------------------------------
# no task schedule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0032_schedule_migrate")]

    def migrate(self):
        self.db.delete_table("sa_taskschedule")
