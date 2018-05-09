# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectProfile config mirror settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models
# NOC modules
from noc.core.model.fields import DocumentReferenceField


class Migration(object):
    def forwards(self):
        Template = db.mock_model(
            model_name='Template',
            db_table='main_template', db_tablespace='',
            pk_field_name='id', pk_field_type=models.AutoField)

        db.add_column(
            "sa_managedobjectprofile",
            "config_mirror_storage",
            DocumentReferenceField(
                "main.ExtStorage",
                null=True, blank=True
            ))
        db.add_column(
            "sa_managedobjectprofile",
            "config_mirror_template",
            models.ForeignKey(
                Template, verbose_name="Config Mirror Template",
                blank=True, null=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "config_mirror_policy",
            models.CharField(
                "Config Mirror Policy",
                max_length=1,
                choices=[
                    ("D", "Disable"),
                    ("A", "Always"),
                    ("C", "Change")
                ],
                default="C"
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "config_validation_policy",
            models.CharField(
                "Config Validation Policy",
                max_length=1,
                choices=[
                    ("D", "Disable"),
                    ("A", "Always"),
                    ("C", "Change")
                ],
                default="C"
            )
        )

    def backwards(self):
        pass
