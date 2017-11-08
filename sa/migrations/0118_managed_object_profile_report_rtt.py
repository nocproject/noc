from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "report_ping_rtt", models.BooleanField(
                "Report RTT",
                default=False
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "report_ping_rtt")
