# ----------------------------------------------------------------------
# schedule migrate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create Any time pattern if not exists
        if (
            self.db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s", ["Any"])[0][0]
            == 0
        ):
            self.db.execute(
                "INSERT INTO main_timepattern(name, description) values(%s,%s)",
                ["Any", "Always match"],
            )
        time_pattern_id = self.db.execute("SELECT id FROM main_timepattern WHERE name=%s", ["Any"])[
            0
        ][0]
        for pn, e, t in self.db.execute(
            "SELECT periodic_name, is_enabled, run_every FROM sa_taskschedule"
        ):
            self.db.execute(
                """INSERT INTO main_schedule(periodic_name, is_enabled, time_pattern_id, run_every)
                VALUES(%s, %s, %s, %s )""",
                [pn, e, time_pattern_id, t],
            )
