from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "weight", models.IntegerField(
                "Alarm weight",
                default=0
            )
        )
        db.delete_column("sa_managedobjectprofile", "check_link_interval")
        db.delete_column("sa_managedobjectprofile", "down_severity")

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "report_ping_rtt")
