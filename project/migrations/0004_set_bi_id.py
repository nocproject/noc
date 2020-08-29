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
    def migrate(self):
        table = "project_project"
        rows = self.db.execute("SELECT id FROM %s WHERE bi_id IS NULL" % table)
        values = ["(%d, %d)" % (r[0], bi_hash(r[0])) for r in rows]
        while values:
            chunk, values = values[:PG_CHUNK], values[PG_CHUNK:]
            self.db.execute(
                """
                UPDATE %s AS t
                SET
                  bi_id = c.bi_id
                FROM (
                  VALUES
                  %s
                ) AS c(id, bi_id)
                WHERE c.id = t.id
                """
                % (table, ",\n".join(chunk))
            )
        self.db.execute("ALTER TABLE %s ALTER bi_id SET NOT NULL" % table)
