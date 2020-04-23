# ----------------------------------------------------------------------
# as name and routes maintainer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "peer_as", "as_name", models.CharField("AS Name", max_length=64, null=True, blank=True)
        )
        Maintainer = self.db.mock_model(model_name="Maintainer", db_table="peer_maintainer")
        self.db.add_column(
            "peer_as",
            "routes_maintainer",
            models.ForeignKey(
                Maintainer,
                verbose_name="Routes Maintainer",
                null=True,
                blank=True,
                related_name="routes_maintainer",
                on_delete=models.CASCADE,
            ),
        )
