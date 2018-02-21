# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Replace pyrule with handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        db.add_column(
            "fm_alarmtrigger",
            "handler",
            models.CharField("Handler",
                             max_length=128, null=True, blank=True)
        )
        db.add_column(
            "fm_alarmtrigger",
            "description",
            models.CharField("Description",
                             max_length=256, null=True, blank=True)
        )
        db.add_column(
            "fm_eventtrigger",
            "description",
            models.CharField("Description",
                             max_length=256, null=True, blank=True)
        )
        # Fill description
        rows = db.execute(
            """SELECT t.id, r.name
            FROM fm_eventtrigger t JOIN main_pyrule r ON (t.pyrule_id = r.id)
            """)
        for t_id, rule_name in rows:
            db.execute(
                """UPDATE fm_eventtrigger
                SET desciption = 'Removed pyRule ' || %s
                WHERE id = %s
                """, [rule_name, t_id]
            )
        rows = db.execute(
            """SELECT t.id, r.name
            FROM fm_alarmtrigger t JOIN main_pyrule r ON (t.pyrule_id = r.id)
            """)
        for t_id, rule_name in rows:
            db.execute(
                """UPDATE fm_alarmtrigger
                SET desciption = 'Removed pyRule ' || %s
                WHERE id = %s
                """, [rule_name, t_id]
            )
        # drop pyrule
        db.drop_column("fm_eventtrigger", "pyrule_id")
        db.drop_column("fm_alarmtrigger", "pyrule_id")

    def backwards(self):
        pass
