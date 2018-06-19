# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
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
            "beef_storage",
            DocumentReferenceField(
                "main.ExtStorage",
                null=True, blank=True
            ))
        db.add_column(
            "sa_managedobjectprofile",
            "beef_path_template",
            models.ForeignKey(
                Template, verbose_name="Config Mirror Template",
                blank=True, null=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "beef_policy",
            models.CharField(
                "Beef Policy",
                max_length=1,
                choices=[
                    ("D", "Disable"),
                    ("A", "Always"),
                    ("C", "Change")
                ],
                default="D"
            )
        )

    def backwards(self):
        pass
