# ----------------------------------------------------------------------
# profile language
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
        self.db.delete_column("main_userprofile", "preferred_language_id")
        self.db.add_column(
            "main_userprofile",
            "preferred_language",
            models.CharField("Preferred Language", max_length=16, null=True, blank=True),
        )
