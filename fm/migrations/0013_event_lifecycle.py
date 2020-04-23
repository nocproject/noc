# ----------------------------------------------------------------------
# event lifecycle
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
        Event = self.db.mock_model(model_name="Event", db_table="fm_event")
        self.db.add_column(
            "fm_event", "status", models.CharField("Status", max_length=1, default="U")
        )
        self.db.add_column(
            "fm_event", "active_till", models.DateTimeField("Active Till", blank=True, null=True)
        )
        self.db.add_column(
            "fm_event",
            "close_timestamp",
            models.DateTimeField("Close Timestamp", blank=True, null=True),
        )
        self.db.add_column(
            "fm_event",
            "root",
            models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE),
        )
