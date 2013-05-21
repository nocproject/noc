# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Project module models
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.create_table("project_project", (
            ("id", models.AutoField(
                verbose_name="ID", primary_key=True,
                auto_created=True)),
            ("code", models.CharField("Code", max_length=256, unique=True)),
            ("name", models.CharField("Name", max_length=256)),
            ("description", models.TextField(
                "Description", null=True, blank=True))
        ))

    def backwards(self):
        db.delete_table("project_project")