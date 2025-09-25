# ----------------------------------------------------------------------
# task schedule
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
        # Model 'TaskSchedule'
        self.db.create_table(
            "sa_taskschedule",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("periodic_name", models.CharField("Periodic Task", max_length=64)),
                ("is_enabled", models.BooleanField("Enabled?", default=False)),
                ("run_every", models.PositiveIntegerField("Run Every (secs)", default=86400)),
                ("retries", models.PositiveIntegerField("Retries", default=1)),
                ("retry_delay", models.PositiveIntegerField("Retry Delay (secs)", default=60)),
                ("timeout", models.PositiveIntegerField("Timeout (secs)", default=300)),
                ("next_run", models.DateTimeField("Next Run", auto_now_add=True)),
                ("retries_left", models.PositiveIntegerField("Retries Left", default=1)),
            ),
        )
