from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        ManagedObject = db.mock_model(
            model_name="ManagedObject",
            db_table="sa_managedobject",
            db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)

        db.add_column(
            "sa_managedobject",
            "controller",
            models.ForeignKey(
                ManagedObject,
                verbose_name="Controller",
                blank=True, null=True
            )
        )
        db.add_column(
            "sa_managedobject",
            "last_seen",
            models.DateTimeField(
                "Last Seen",
                blank=True, null=True
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobject", "controller_id")
        db.delete_column("sa_managedobject", "last_seen")
