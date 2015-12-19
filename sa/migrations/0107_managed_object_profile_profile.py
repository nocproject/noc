# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_profile",
            models.BooleanField(default=True)
        )

    def backwards(self):
        pass
