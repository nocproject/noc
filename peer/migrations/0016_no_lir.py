# ----------------------------------------------------------------------
# no lir
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party models
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        Maintainer = self.db.mock_model(model_name="Maintainer", db_table="peer_maintainer")

        rir_id = self.db.execute("SELECT id FROM peer_rir LIMIT 1")[0][0]
        lir_to_rir = {}
        for lir_id, name in self.db.execute("SELECT id,name FROM peer_lir"):
            self.db.execute(
                "INSERT INTO peer_maintainer(maintainer,description,auth,rir_id) VALUES(%s,%s,%s,%s)",
                [name, name, "NOAUTH", rir_id],
            )
            lir_to_rir[lir_id] = self.db.execute(
                "SELECT id FROM peer_maintainer WHERE maintainer=%s", [name]
            )[0][0]
        self.db.add_column(
            "peer_as",
            "maintainer",
            models.ForeignKey(
                Maintainer,
                verbose_name="Maintainer",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
        for as_id, lir_id in self.db.execute("SELECT id,lir_id FROM peer_as"):
            self.db.execute(
                "UPDATE peer_as SET maintainer_id=%s WHERE id=%s", [lir_to_rir[lir_id], as_id]
            )
        self.db.execute("ALTER TABLE peer_as ALTER maintainer_id SET NOT NULL")
        self.db.delete_column("peer_as", "lir_id")
        self.db.delete_table("peer_lir")
