# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# prefix ip discovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column(
            "ip_prefix", "enable_ip_discovery",
            models.CharField(
                "Enable IP Discovery",
                max_length=1,
                choices=[("I", "Inherit"), ("E", "Enable"), ("D", "Disable")],
                default="I",
                blank=False,
                null=False
            )
        )

    def backwards(self):
        db.drop_column("ip_prefix", "enable_ip_discovery")
