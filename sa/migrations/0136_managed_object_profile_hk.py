# -*- coding: utf-8 -*-
from south.db import db
from django.db import models


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
