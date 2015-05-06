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
    def forwards(self):
        db.add_column(
            "ip_ippool",
            "name",
            models.CharField(
                "Pool Name",
                max_length=64, default="default"
            )
        )

    def backwards(self):
        db.drop_column("ip_ippool", "name")
