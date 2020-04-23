# ----------------------------------------------------------------------
# rule drop event
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "fm_eventclassificationrule",
            "drop_event",
            models.BooleanField("Drop Event", default=False),
        )
