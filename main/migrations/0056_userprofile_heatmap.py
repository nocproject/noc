# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# userprofile heatmap
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column("main_userprofile", "heatmap_lon", models.FloatField("Longitude", blank=True, null=True))
        db.add_column("main_userprofile", "heatmap_lat", models.FloatField("Latitude", blank=True, null=True))
        db.add_column("main_userprofile", "heatmap_zoom", models.IntegerField("Zoom", blank=True, null=True))

    def backwards(self):
        db.delete_column("main_userprofile", "heatmap_lon")
        db.delete_column("main_userprofile", "heatmap_lat")
        db.delete_column("main_userprofile", "heatmap_zoom")
