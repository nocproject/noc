# ---------------------------------------------------------------------
# VRF, Prefix, Address .project field
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate_project(self, table):
        r = self.db.execute(
            f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE project IS NOT NULL AND project != ''"""
        )[0][0]
        if r:
            # Create custom field
            self.db.execute(
                """
            INSERT INTO main_customfield("table", name, is_active,
                label, "type", max_length, is_indexed)
            VALUES(%s, 'project', TRUE, 'Project', 'str', 256, TRUE)
            """,
                [table],
            )

            # Move data
            self.db.execute(
                f"""
                ALTER TABLE {table} RENAME project TO cust_project
            """
            )
        else:
            # Drop column
            self.db.delete_column(table, "project")

    def migrate(self) -> None:
        self.migrate_project("ip_vrf")
        self.migrate_project("ip_prefix")
        self.migrate_project("ip_address")
