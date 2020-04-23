# ----------------------------------------------------------------------
# snippet confirmation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0035_prefix_table")]

    def migrate(self):
        self.db.add_column(
            "sa_commandsnippet",
            "require_confirmation",
            models.BooleanField("Require Confirmation", default=False),
        )
