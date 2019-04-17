# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Add direct_permission field to prefix
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        AdministrativeDomain = db.mock_model(
            model_name="AdministrativeDomain",
            db_table="sa_administrativedomain", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        db.add_column(
            "ip_address", "administrative_domain",
            models.ForeignKey(
                AdministrativeDomain, verbose_name="Administrative Domain",
                null=True, blank=True))

        db.execute("ALTER TABLE ip_vrf ADD COLUMN direct_permissions  JSONB")
        db.execute("ALTER TABLE ip_prefix ADD COLUMN direct_permissions  JSONB")
        db.execute("ALTER TABLE ip_address ADD COLUMN direct_permissions  JSONB")

    def backwards(self):
        db.drop_column("ip_address", "sa_administrativedomain_id")
        for t in ["ip_vrf", "ip_prefix", "ip_address"]:
            db.drop_column(t, "direct_permissions")
