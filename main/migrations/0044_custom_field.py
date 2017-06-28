# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Create CustomField
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from django.db import models


class Migration:
    def forwards(self):
        # ResourceState
        db.create_table("main_customfield", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True,
                                    auto_created=True)),
            ("table", models.CharField("Table", max_length=64)),
            ("name", models.CharField("Name", max_length=64)),
            ("is_active", models.BooleanField("Is Active", default=True)),
            ("label", models.CharField("Label", max_length=128)),
            ("type", models.CharField("Type", max_length=64,
                                      choices=[
                                          ("str", "String"),
                                          ("int", "Integer")
                                      ])),
            ("description", models.TextField("Description",
                                             null=True, blank=True)),
            ("max_length", models.IntegerField("Max. Length", default=0)),
            ("regexp", models.CharField("Regexp", max_length=256,
                                        null=True, blank=True)),
            ("is_indexed", models.BooleanField("Is Indexed", default=False)),
            ("is_searchable", models.BooleanField("Is Searchable",
                                                  default=False)),
            ("is_filtered", models.BooleanField("Is Filtered", default=False))
        ))
        db.send_create_signal("main", ["CustomField"])

    def backwards(self):
        db.delete_table("main_customfield")
