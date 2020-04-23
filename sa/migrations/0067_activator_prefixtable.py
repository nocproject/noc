# ----------------------------------------------------------------------
# activator prefixtable
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.ip import IPv4


class Migration(BaseMigration):
    depends_on = [("main", "0035_prefix_table")]

    def migrate(self):
        PrefixTable = self.db.mock_model(model_name="PrefixTable", db_table="main_prefixtable")
        self.db.add_column(
            "sa_activator",
            "prefix_table",
            models.ForeignKey(
                PrefixTable,
                verbose_name="Prefix Table",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
        # Migrate data
        for id, name, ip, to_ip in self.db.execute("SELECT id, name, ip, to_ip FROM sa_activator"):
            pt_name = "Activator::%s" % name
            self.db.execute(
                """
                INSERT INTO main_prefixtable(name)
                VALUES(%s)
                """,
                [pt_name],
            )
            (pt_id,) = self.db.execute(
                "SELECT id FROM main_prefixtable WHERE name = %s", [pt_name]
            )[0]
            for p in IPv4.range_to_prefixes(ip, to_ip):
                self.db.execute(
                    """
                    INSERT INTO main_prefixtableprefix(table_id, afi, prefix)
                    VALUES(%s, '4', %s)
                    """,
                    [pt_id, p.prefix],
                )
            self.db.execute("UPDATE sa_activator SET prefix_table_id=%s WHERE id=%s", [pt_id, id])
