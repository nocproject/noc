# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# shard
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
        db.create_table(
            "main_shard", (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=128, unique=True)),
                ("is_active", models.BooleanField("Is Active", default=True)),
                ("description", models.TextField("Description", null=True, blank=True)),
            )
        )
        db.send_create_signal("main", ["Shard"])

    def backwards(self):
        db.delete_table("main_shard")
