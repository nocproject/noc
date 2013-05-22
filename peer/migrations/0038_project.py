# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AS.project and Peer.project
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
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
        # Create .project
        Project = db.mock_model(
            model_name="Project",
            db_table="project_project", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        for t in ("peer_as", "peer_peer"):
            db.add_column(
                t, "project",
                models.ForeignKey(
                    Project, verbose_name="Project",
                    null=True, blank=True))

    def backwards(self):
        for t in ("peer_as", "peer_peer"):
            db.drop_column(t, "project_id")
