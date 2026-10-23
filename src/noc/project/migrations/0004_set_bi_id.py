# ----------------------------------------------------------------------
# Initialize bi_id field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash

PG_CHUNK = 500


class Migration(BaseMigration):
    def migrate(self) -> None:
        table = "project_project"
        rows = self.db.execute(f"SELECT id FROM {table} WHERE bi_id IS NULL")
        values = [f"({int(r[0])}, {int(bi_hash(r[0]))})" for r in rows]
        while values:
            chunk, values = values[:PG_CHUNK], values[PG_CHUNK:]
            self.db.execute(
                """
                UPDATE {} AS t
                SET
                  bi_id = c.bi_id
                FROM (
                  VALUES
                  {}
                ) AS c(id, bi_id)
                WHERE c.id = t.id
                """.format(table, ",\n".join(chunk))
            )
        self.db.execute(f"ALTER TABLE {table} ALTER bi_id SET NOT NULL")
