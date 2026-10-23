# ----------------------------------------------------------------------
# ip integration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField
from noc.core.bi.decorator import bi_hash

PG_CHUNK = 500


class Migration(BaseMigration):
    def migrate(self) -> None:
        # IP Models
        TABLES = ["ip_vrf", "ip_prefix", "ip_address"]
        for table in TABLES:
            self.db.add_column(
                table,
                "remote_system",
                DocumentReferenceField("self", null=True, blank=True),
            )
            self.db.add_column(
                table,
                "remote_id",
                models.CharField(max_length=64, null=True, blank=True),
            )
            self.db.add_column(table, "bi_id", models.BigIntegerField(null=True, blank=True))
        # Set BI_ID
        for table in TABLES:
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
