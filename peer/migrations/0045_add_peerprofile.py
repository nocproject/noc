# ----------------------------------------------------------------------
# Add PeerProfile And migrate data from peer Group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson
from django.db import models

# NOC module
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    WF_DEFAULT = "676509728db9f670c21e14d4"

    depends_on = [("wf", "0014_add_peer_default_workflow")]

    def migrate(self):
        # Model 'PeerGroup'
        self.db.create_table(
            "peer_peerprofile",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("description", models.CharField("Description", max_length=64)),
                ("workflow", DocumentReferenceField("wf.Workflow", null=False, blank=False)),
                ("max_prefixes", models.IntegerField("Max. Prefixes", default=100)),
                (
                    "data",
                    models.JSONField("Data", null=True, blank=True, default=lambda: "[]"),
                ),
                (
                    "status_discovery",
                    models.CharField(
                        choices=[
                            ("d", "Disabled"),
                            ("e", "Enable"),
                            ("c", "Clear Alarm"),
                            ("ca", "Clear Alarm if Admin Down"),
                            ("rc", "Raise & Clear Alarm"),
                        ],
                        default="d",
                        max_length=2,
                    ),
                ),
                (
                    "status_change_notification",
                    models.CharField(
                        choices=[
                            ("d", "Disabled"),
                            ("c", "Changed Message"),
                            ("f", "All Message"),
                        ],
                        default="d",
                        max_length=1,
                    ),
                ),
            ),
        )
        for id, n, d, comm, m_pref, local_pref, i_med, e_med in self.db.execute(
            """
                SELECT id, name, description, communities, max_prefixes, local_pref, import_med, export_med
                FROM peer_peergroup
         """
        ):
            data = []
            for name, value in [
                ("communities", comm),
                ("local_pref", local_pref),
                ("import_med", i_med),
                ("export_med", e_med),
            ]:
                if value:
                    data.append({"name": name, "value": value})
            self.db.execute(
                "INSERT INTO peer_peerprofile(id,name,description,workflow,max_prefixes,data)"
                " VALUES(%s,%s,%s,%s,%s,%s::jsonb)",
                [id, n, d, self.WF_DEFAULT, m_pref, orjson.dumps(data).decode()],
            )
        PeerProfile = self.db.mock_model(model_name="PeerProfile", db_table="peer_peerprofile")
        self.db.add_column(
            "peer_peer",
            "profile",
            models.ForeignKey(PeerProfile, null=True, on_delete=models.CASCADE),
        )
        self.db.execute("UPDATE peer_peer SET profile_id=peer_group_id")
        self.db.execute("UPDATE peer_peer SET profile_id=1 WHERE profile_id is NULL")
        self.db.delete_column("peer_peer", "peer_group_id")
