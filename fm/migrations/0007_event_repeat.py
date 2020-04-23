# ----------------------------------------------------------------------
# event repeat
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
        # Mock Models
        Event = self.db.mock_model(model_name="Event", db_table="fm_event")

        # Model 'EventRepeat'
        self.db.create_table(
            "fm_eventrepeat",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("event", models.ForeignKey(Event, verbose_name="Event", on_delete=models.CASCADE)),
                ("timestamp", models.DateTimeField("Timestamp")),
            ),
        )
        # Mock Models
        EventClass = self.db.mock_model(model_name="EventClass", db_table="fm_eventclass")

        # Model 'EventClassVar'
        self.db.create_table(
            "fm_eventclassvar",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "event_class",
                    models.ForeignKey(
                        EventClass, verbose_name="Event Class", on_delete=models.CASCADE
                    ),
                ),
                ("name", models.CharField("Name", max_length=64)),
                ("required", models.BooleanField("Required", default=True)),
                ("repeat_suppression", models.BooleanField("Repeat Suppression", default=False)),
            ),
        )
        self.db.create_index("fm_eventclassvar", ["event_class_id", "name"], unique=True)

        self.db.add_column(
            "fm_eventclass",
            "repeat_suppression",
            models.BooleanField("Repeat Suppression", default=False),
        )
        self.db.add_column(
            "fm_eventclass",
            "repeat_suppression_interval",
            models.IntegerField("Repeat Suppression interval (secs)", default=3600),
        )
        # Migrate variables
        for id, vars in self.db.execute("SELECT id,variables FROM fm_eventclass"):
            if vars:
                for v in [v.strip() for v in vars.split(",")]:
                    self.db.execute(
                        """INSERT INTO fm_eventclassvar(event_class_id,name,required,repeat_suppression)
                           VALUES(%s,%s,true,false)""",
                        [id, v],
                    )
        self.db.delete_column("fm_eventclass", "variables")
