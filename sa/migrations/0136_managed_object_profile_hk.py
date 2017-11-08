# -*- coding: utf-8 -*-
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_mac",
            models.BooleanField(default=False)
        )

        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_hk",
            models.BooleanField(default=False)
        )

        db.add_column(
            "sa_managedobjectprofile",
            "hk_handler",
            models.CharField(
                "Housekeeping Handler",
                max_length=255,
                null=True, blank=True
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "enable_box_discovery_mac")
        db.delete_column("sa_managedobjectprofile",
                         "enable_box_discovery_hk")
        db.delete_column("sa_managedobjectprofile",
                         "hk_handler")
