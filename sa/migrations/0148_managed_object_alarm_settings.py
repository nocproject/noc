from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        # Profile settings
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_alarm_policy",
            models.CharField(
                "Box Discovery Alarm Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="E"
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_alarm_policy",
            models.CharField(
                "Periodic Discovery Alarm Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="E"
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_fatal_alarm_weight",
            models.IntegerField(
                "Box Fatal Alarm Weight",
                default=10
            )
        )

        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_alarm_weight",
            models.IntegerField(
                "Box Alarm Weight",
                default=1
            )
        )

        db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_fatal_alarm_weight",
            models.IntegerField(
                "Box Fatal Alarm Weight",
                default=10
            )
        )

        db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_alarm_weight",
            models.IntegerField(
                "Periodic Alarm Weight",
                default=1
            )
        )

        # Object settings
        db.add_column(
            "sa_managedobject",
            "box_discovery_alarm_policy",
            models.CharField(
                "Box Discovery Alarm Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable"),
                    ("P", "From Profile")
                ],
                default="P"
            )
        )
        db.add_column(
            "sa_managedobject",
            "periodic_discovery_alarm_policy",
            models.CharField(
                "Periodic Discovery Alarm Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable"),
                    ("P", "From Profile")
                ],
                default="P"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "box_discovery_alarm_policy")
        db.delete_column("sa_managedobjectprofile",
                         "periodic_discovery_alarm_policy")
        db.delete_column("sa_managedobjectprofile",
                         "box_discovery_fatal_alarm_weight")
        db.delete_column("sa_managedobjectprofile",
                         "box_discovery_alarm_weight")
        db.delete_column("sa_managedobjectprofile",
                         "periodic_discovery_fatal_alarm_weight")
        db.delete_column("sa_managedobjectprofile",
                         "periodic_discovery_alarm_weight")
        db.delete_column("sa_managedobject",
                         "box_discovery_alarm_policy")
        db.delete_column("sa_managedobject",
                         "periodic_discovery_alarm_policy")
