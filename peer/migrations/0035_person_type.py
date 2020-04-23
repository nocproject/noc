# ----------------------------------------------------------------------
# person type
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
            "peer_person",
            "type",
            models.CharField(
                "type", max_length=1, default="P", choices=[("P", "Person"), ("R", "Role")]
            ),
        )
