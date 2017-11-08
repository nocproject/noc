from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_cpe",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "cpe_segment_policy",
            models.CharField(
                "CPE Segment Policy",
                max_length=1,
                choices=[
                    ("C", "From controller"),
                    ("L", "From linked object")
                ],
                default="C"
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "cpe_cooldown",
            models.IntegerField(
                "CPE cooldown, days",
                default=0
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "enable_box_discovery_cpe")
        db.delete_column("sa_managedobjectprofile",
                         "cpe_segment_policy")
        db.delete_column("sa_managedobjectprofile",
                         "cpe_cooldown")
