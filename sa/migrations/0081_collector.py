# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        # Model "Collector"
        db.create_table("sa_collector", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True,
                                    auto_created=True)),
            ("name",
             models.CharField("Name", max_length=64, unique=True)),
            ("is_active", models.BooleanField("Is Active", default=True)),
            ("description", models.TextField("Description", null=True, blank=True))
        ))
        db.send_create_signal("sa", ["Collector"])
        Collector = db.mock_model(model_name="Collector",
            db_table="sa_collector", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        db.add_column("sa_managedobject", "collector",
            models.ForeignKey(Collector,
                verbose_name="Collector",
                null=True, blank=True
        ))

    def backwards(self):
        db.delete_column("sa_managedobject", "collector_id")
        db.delete_table("sa_collector")
