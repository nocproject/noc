# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# VRF.project, Prefix.project, IP.project
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
=======
##----------------------------------------------------------------------
## VRF.project, Prefix.project, IP.project
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "ip_prefix",
            "enable_ip_discovery",
            models.CharField(
                "Enable IP Discovery",
                max_length=1,
                choices=[
                    ("I", "Inherit"),
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="I",
                blank=False,
                null=False
            )
        )

    def backwards(self):
        db.drop_column("ip_prefix", "enable_ip_discovery")
