from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobject",
            "local_cpe_id",
            models.CharField(
                "Local CPE ID",
                max_length=128,
                null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobject",
            "global_cpe_id",
            models.CharField(
                "Global CPE ID",
                max_length=128,
                null=True, blank=True
            )
        )
        db.create_index("sa_managedobject", ["local_cpe_id"],
                        unique=False, db_tablespace="")
        db.create_index("sa_managedobject", ["global_cpe_id"],
                        unique=True, db_tablespace="")

    def backwards(self):
        db.delete_column("sa_managedobject", "local_cpe_id")
        db.delete_column("sa_managedobject", "global_cpe_id")
