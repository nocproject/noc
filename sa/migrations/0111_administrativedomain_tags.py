# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db
from noc.core.model.fields import TagsField


class Migration:
    def forwards(self):
        AdministrativeDomain = db.mock_model(
            model_name="AdministrativeDomain",
            db_table="sa_administrativedomain", db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        db.add_column(
            "sa_administrativedomain",
            "tags",
            TagsField("Tags", null=True, blank=True)
        )
        db.add_column(
            "sa_administrativedomain",
            "parent",
            models.ForeignKey(AdministrativeDomain,
                              verbose_name="Parent", null=True,
                              blank=True)
        )


def backwards(self):
    pass
