# ----------------------------------------------------------------------
# events
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

        # Model 'EventPriority'
        self.db.create_table(
            "fm_eventpriority",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("priority", models.IntegerField("Priority")),
                ("description", models.TextField("Description", blank=True, null=True)),
            ),
        )
        # Model 'EventCategory'
        self.db.create_table(
            "fm_eventcategory",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("description", models.TextField("Description", blank=True, null=True)),
            ),
        )
        # Mock Models
        EventPriority = self.db.mock_model(model_name="EventPriority", db_table="fm_eventpriority")
        EventCategory = self.db.mock_model(model_name="EventCategory", db_table="fm_eventcategory")

        # Model 'EventClass'
        self.db.create_table(
            "fm_eventclass",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64)),
                (
                    "category",
                    models.ForeignKey(
                        EventCategory, verbose_name="Event Category", on_delete=models.CASCADE
                    ),
                ),
                (
                    "default_priority",
                    models.ForeignKey(
                        EventPriority, verbose_name="Default Priority", on_delete=models.CASCADE
                    ),
                ),
                ("variables", models.CharField("Variables", max_length=128, blank=True, null=True)),
                ("subject_template", models.CharField("Subject Template", max_length=128)),
                ("body_template", models.TextField("Body Template")),
                ("last_modified", models.DateTimeField("last_modified", auto_now=True)),
            ),
        )
        # Mock Models
        EventClass = self.db.mock_model(model_name="EventClass", db_table="fm_eventclass")

        # Model 'EventClassificationRule'
        self.db.create_table(
            "fm_eventclassificationrule",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "event_class",
                    models.ForeignKey(
                        EventClass, verbose_name="Event Class", on_delete=models.CASCADE
                    ),
                ),
                ("name", models.CharField("Name", max_length=64)),
                ("preference", models.IntegerField("Preference", default=1000)),
            ),
        )

        # Mock Models
        EventClassificationRule = self.db.mock_model(
            model_name="EventClassificationRule", db_table="fm_eventclassificationrule"
        )

        # Model 'EventClassificationRE'
        self.db.create_table(
            "fm_eventclassificationre",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "rule",
                    models.ForeignKey(
                        EventClassificationRule,
                        verbose_name="Event Classification Rule",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("left_re", models.CharField("Left RE", max_length=256)),
                ("right_re", models.CharField("Right RE", max_length=256)),
            ),
        )

        # Mock Models
        ManagedObject = self.db.mock_model(model_name="ManagedObject", db_table="sa_managedobject")
        Event = self.db.mock_model(model_name="Event", db_table="fm_event")

        # Model 'Event'
        self.db.create_table(
            "fm_event",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("timestamp", models.DateTimeField("Timestamp")),
                (
                    "managed_object",
                    models.ForeignKey(
                        ManagedObject, verbose_name="Managed Object", on_delete=models.CASCADE
                    ),
                ),
                (
                    "event_priority",
                    models.ForeignKey(
                        EventPriority, verbose_name="Priority", on_delete=models.CASCADE
                    ),
                ),
                (
                    "event_category",
                    models.ForeignKey(
                        EventCategory, verbose_name="Event Class", on_delete=models.CASCADE
                    ),
                ),
                (
                    "event_class",
                    models.ForeignKey(
                        EventClass, verbose_name="Event Class", on_delete=models.CASCADE
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        Event,
                        verbose_name="Parent",
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                ("subject", models.CharField("Subject", max_length=256, null=True, blank=True)),
                ("body", models.TextField("Body", null=True, blank=True)),
            ),
        )

        # Mock Models
        Event = self.db.mock_model(model_name="Event", db_table="fm_event")

        # Model 'EventData'
        self.db.create_table(
            "fm_eventdata",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("event", models.ForeignKey(Event, verbose_name=Event, on_delete=models.CASCADE)),
                ("key", models.CharField("Key", max_length=64)),
                ("value", models.TextField("Value", blank=True, null=True)),
                (
                    "type",
                    models.CharField(
                        "Type",
                        max_length=1,
                        choices=[(">", "Received"), ("V", "Variable"), ("R", "Resolved")],
                        default=">",
                    ),
                ),
            ),
        )
        self.db.create_index("fm_eventdata", ["event_id", "key", "type"], unique=True)
