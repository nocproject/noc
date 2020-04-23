# ----------------------------------------------------------------------
# userprofile heatmap
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "main_userprofile", "heatmap_lon", models.FloatField("Longitude", blank=True, null=True)
        )
        self.db.add_column(
            "main_userprofile", "heatmap_lat", models.FloatField("Latitude", blank=True, null=True)
        )
        self.db.add_column(
            "main_userprofile", "heatmap_zoom", models.IntegerField("Zoom", blank=True, null=True)
        )
