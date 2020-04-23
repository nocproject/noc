# ----------------------------------------------------------------------
# dnszonerecord migrate prio
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        for id, content in self.db.execute(
            """
                SELECT r.id, r.right
                FROM dns_dnszonerecord r
                JOIN dns_dnszonerecordtype t ON (r.type_id = t.id)
                WHERE t.type IN ('MX', 'SRV') """
        ):
            if " " not in content:
                continue
            prio, rest = content.split(" ", 1)
            try:
                prio = int(prio)
            except ValueError:
                continue
            self.db.execute(
                """
                UPDATE dns_dnszonerecord
                SET
                    priority = %s,
                    "right" = %s
                WHERE id = %s
            """,
                [prio, rest, id],
            )
