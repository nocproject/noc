# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VRF.source
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column(
            "ip_vrf",
            "source",
            models.CharField(
                "Source",
                max_length=1,
                choices=[
                    ("M", "Manual"),
                    ("i", "Interface"),
                    ("m", "MPLS")
                ],
                null=False, blank=False,
                default="M"
            )
        )

    def backwards(self):
        pass
