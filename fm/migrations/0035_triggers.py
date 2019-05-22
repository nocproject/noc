# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# triggers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    depends_on = (("main", "0037_template"),)

    def migrate(self):
        Template = self.db.mock_model(
            model_name="Template",
            db_table="main_template",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        TimePattern = self.db.mock_model(
            model_name="TimePattern",
            db_table="main_timepattern",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        NotificationGroup = self.db.mock_model(
            model_name="NotificationGroup",
            db_table="main_notificationgroup",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        PyRule = self.db.mock_model(
            model_name="PyRule",
            db_table="main_pyrule",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        self.db.create_table(
            "fm_eventtrigger", (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("is_enabled", models.BooleanField("Is Enabled", default=True)),
                ("event_class_re", models.CharField("Event class RE", max_length=256)),
                ("condition", models.CharField("Condition", max_length=256, default="True")),
                ("time_pattern", models.ForeignKey(TimePattern, verbose_name="Time Pattern", null=True, blank=True)), (
                    "selector",
                    models.ForeignKey(
                        ManagedObjectSelector, verbose_name="Managed Object Selector", null=True, blank=True
                    )
                ), (
                    "notification_group",
                    models.ForeignKey(NotificationGroup, verbose_name="Notification Group", null=True, blank=True)
                ), ("template", models.ForeignKey(Template, verbose_name="Template", null=True, blank=True)),
                ("pyrule", models.ForeignKey(PyRule, verbose_name="pyRule", null=True, blank=True))
            )
        )

        self.db.create_table(
            "fm_alarmtrigger", (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("is_enabled", models.BooleanField("Is Enabled", default=True)),
                ("alarm_class_re", models.CharField("Alarm class RE", max_length=256)),
                ("condition", models.CharField("Condition", max_length=256, default="True")),
                ("time_pattern", models.ForeignKey(TimePattern, verbose_name="Time Pattern", null=True, blank=True)), (
                    "selector",
                    models.ForeignKey(
                        ManagedObjectSelector, verbose_name="Managed Object Selector", null=True, blank=True
                    )
                ), (
                    "notification_group",
                    models.ForeignKey(NotificationGroup, verbose_name="Notification Group", null=True, blank=True)
                ), ("template", models.ForeignKey(Template, verbose_name="Template", null=True, blank=True)),
                ("pyrule", models.ForeignKey(PyRule, verbose_name="pyRule", null=True, blank=True))
            )
        )
