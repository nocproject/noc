# ----------------------------------------------------------------------
# Add PeerProfile And migrate data from peer Group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC module
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    WF_DEFAULT_STATE = "67650a398db9f670c21e14d6"

    def migrate(self):
        # Remote Constraint
        non_required_columns = ["peering_point_id", "local_ip"]
        for column in non_required_columns:
            self.db.execute(f"ALTER TABLE peer_peer ALTER {column} DROP NOT NULL")
        self.db.execute("ALTER TABLE peer_peer ALTER import_filter SET DEFAULT 'any'")
        self.db.execute("ALTER TABLE peer_peer ALTER export_filter SET DEFAULT 'any'")
        ManagedObject = self.db.mock_model(model_name="ManagedObject", db_table="sa_managedobject")
        self.db.add_column(
            "peer_peer",
            "managed_object",
            models.ForeignKey(ManagedObject, null=True, on_delete=models.CASCADE),
        )
        # Workflow
        # Create new ManagedObject.state
        self.db.add_column(
            "peer_peer", "state", DocumentReferenceField("wf.State", null=True, blank=True)
        )
        columns = {
            "state_changed": "State Changed",
            "expired": "Expired",
            "last_seen": "Last Seen",
            "first_discovered": "First Discovered",
        }
        for column, column_title in columns.items():
            self.db.add_column(
                "peer_peer",
                column,
                models.DateTimeField(column_title, blank=True, null=True),
            )
        # Create index
        self.db.create_index("peer_peer", ["state"])
        for status, wf in [
            ("P", "67650a398db9f670c21e14d6"),
            ("A", "67650ae68db9f670c21e14d8"),
            ("S", "67650a73d65c734a17bc046f"),
        ]:
            self.db.execute("UPDATE peer_peer SET state=%s WHERE status = %s", params=[wf, status])
        self.db.execute(
            "UPDATE peer_peer SET state=%s WHERE state is NULL", params=[self.WF_DEFAULT_STATE]
        )
        self.db.delete_column("peer_peer", "status")
        # Oper Columns
        self.db.add_column(
            "peer_peer",
            "oper_status",
            models.IntegerField(
                choices=[
                    (1, "idle"),
                    (2, "connect"),
                    (3, "active"),
                    (4, "opensent"),
                    (5, "openconfirm"),
                    (6, "established"),
                ],
                null=True,
            ),
        )
        self.db.add_column(
            "peer_peer", "oper_status_change", models.DateTimeField(null=True, blank=True)
        )
