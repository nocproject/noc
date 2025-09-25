# ----------------------------------------------------------------------
# Migrate ManagedObjectProfile MatchRules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "match_rules",
            models.JSONField("Match Dynamic Rules", null=True, blank=True, default=lambda: "[]"),
        )
