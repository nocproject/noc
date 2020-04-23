# ----------------------------------------------------------------------
# Replace pyrule with handlers
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
            "fm_alarmtrigger",
            "handler",
            models.CharField("Handler", max_length=128, null=True, blank=True),
        )
        self.db.add_column(
            "fm_alarmtrigger",
            "description",
            models.CharField("Description", max_length=256, null=True, blank=True),
        )
        self.db.add_column(
            "fm_eventtrigger",
            "description",
            models.CharField("Description", max_length=256, null=True, blank=True),
        )
        # Fill description
        rows = self.db.execute(
            """SELECT t.id, r.name
            FROM fm_eventtrigger t JOIN main_pyrule r ON (t.pyrule_id = r.id)
            """
        )
        for t_id, rule_name in rows:
            self.db.execute(
                """UPDATE fm_eventtrigger
                SET description = 'Removed pyRule ' || %s
                WHERE id = %s
                """,
                [rule_name, t_id],
            )
        rows = self.db.execute(
            """SELECT t.id, r.name
            FROM fm_alarmtrigger t JOIN main_pyrule r ON (t.pyrule_id = r.id)
            """
        )
        for t_id, rule_name in rows:
            self.db.execute(
                """UPDATE fm_alarmtrigger
                SET description = 'Removed pyRule ' || %s
                WHERE id = %s
                """,
                [rule_name, t_id],
            )
        # drop pyrule
        self.db.delete_column("fm_eventtrigger", "pyrule_id")
        self.db.delete_column("fm_alarmtrigger", "pyrule_id")
