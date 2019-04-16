# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# template
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
            "main_template", (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", unique=True, max_length=128)),
                ("subject", models.TextField("Subject")),
                ("body", models.TextField("Body")),
            )
        )

        Template = db.mock_model(
            model_name="Template",
            db_table="main_template",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        db.create_table(
            "main_systemtemplate", (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("description", models.TextField("Description", null=True, blank=True)),
                ("template", models.ForeignKey(Template, verbose_name="Template")),
            )
        )

        db.send_create_signal("main", ["Template", "SystemTemplate"])

    def backwards(self):
        db.delete_table("main_systemtemplate")
        db.delete_table("main_template")
