# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# *.*_discovery_policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.drop_column(
            "ip_prefix",
            "enable_ip_discovery"
        )
        db.add_column(
            "ip_prefix",
            "prefix_discovery_policy",
            models.CharField(
                "Prefix Discovery Policy",
                max_length=1,
                choices=[
                    ("P", "Profile"),
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="P",
                blank=False,
                null=False
            )
        )
        db.add_column(
            "ip_prefix",
            "address_discovery_policy",
            models.CharField(
                "Address Discovery Policy",
                max_length=1,
                choices=[
                    ("P", "Profile"),
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="P",
                blank=False,
                null=False
            )
        )

    def backwards(self):
        pass
