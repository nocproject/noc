# ----------------------------------------------------------------------
# default time pattern
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

TIME_PATTERNS = [("Any", "Always match", []), ("Workdays", "Match workdays", ["mon-fri"])]


class Migration(BaseMigration):
    def migrate(self):
        for name, desc, tpd in TIME_PATTERNS:
            if (
                self.db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s", [name])[0][0]
                == 0
            ):
                self.db.execute(
                    "INSERT INTO main_timepattern(name,description) VALUES(%s,%s)", [name, desc]
                )
                tp_id = self.db.execute("SELECT id FROM main_timepattern WHERE name=%s", [name])[0][
                    0
                ]
                for tp in tpd:
                    self.db.execute(
                        "INSERT INTO main_timepatternterm(time_pattern_id,term) VALUES(%s,%s)",
                        [tp_id, tp],
                    )
