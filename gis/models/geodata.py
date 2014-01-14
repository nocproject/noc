# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Point object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.gis.db import models


class GeoData(models.Model):
    class Meta:
        verbose_name = "Geo Data"
        verbose_name_plural = "Geo Data"
        app_label = "gis"
        db_table = "gis_geodata"

    # Layer id
    layer = models.CharField(max_length=24, db_index=True)
    # Inventory Object's ObjectId
    object = models.CharField(max_length=24, db_index=True)
    #
    label = models.CharField(max_length=64, null=True, blank=True)
    # Spatial data
    data = models.GeometryField()
    #
    objects = models.GeoManager()

    def __unicode__(self):
        return self.label or self.object