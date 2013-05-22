# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VRF.project, Prefix.project, IP.project
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    depends_on = (
        ("project", "0001_initial"),
    )

    def forwards(self):
        # Create .state
        Project = db.mock_model(
            model_name="Project",
            db_table="project_project", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        for t in ["ip_vrf", "ip_prefix", "ip_address"]:
            db.add_column(
                t, "project",
                models.ForeignKey(
                    Project, verbose_name="Project",
                    null=True, blank=True))

    def backwards(self):
        for t in ["ip_vrf", "ip_prefix", "ip_address"]:
            db.drop_column(t, "project_id")
