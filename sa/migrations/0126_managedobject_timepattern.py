from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        TimePattern = db.mock_model(model_name="TimePattern", db_table="main_timepattern",
                                    db_tablespace="", pk_field_name="id", pk_field_type=models.AutoField)
        db.add_column("sa_managedobject",
                      "time_pattern", models.ForeignKey(TimePattern, null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "time_pattern_id")
