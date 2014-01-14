# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.gis.db import models
## Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.create_table("gis_geodata", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("layer", models.CharField(max_length=36)),
            ("label", models.CharField(max_length=64, null=True, blank=True)),
            ("object", models.CharField(max_length=24)),
            ("data", models.GeometryField())
        ))
        db.send_create_signal("gis", ["GeoData"])
        db.create_index("gis_geodata", ["layer"])
        db.create_index("gis_geodata", ["object"])

    def backwards(self):
        db.drop_table("gis_geodata")
