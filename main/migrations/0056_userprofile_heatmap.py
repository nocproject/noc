# -*- coding: utf-8 -*-

from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "main_userprofile",
            "heatmap_lon",
            models.FloatField("Longitude", blank=True, null=True))
        db.add_column(
            "main_userprofile",
            "heatmap_lat",
            models.FloatField("Latitude", blank=True, null=True))
        db.add_column(
            "main_userprofile",
            "heatmap_zoom",
            models.IntegerField("Zoom", blank=True, null=True))

    def backwards(self):
        db.delete_column("main_userprofile", "heatmap_lon")
        db.delete_column("main_userprofile", "heatmap_lat")
        db.delete_column("main_userprofile", "heatmap_zoom")
