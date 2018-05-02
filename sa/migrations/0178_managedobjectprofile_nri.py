# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NRI discovery settings
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
            "sa_managedobjectprofile",
            "enable_box_discovery_nri_portmap",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_nri_service",
            models.BooleanField(default=False)
        )

    def backwards(self):
        pass
