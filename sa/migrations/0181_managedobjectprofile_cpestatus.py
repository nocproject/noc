# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectProfile.enable_box_discovery_cpestatus
# ManagedObjectProfile.enable_periodic_discovery_cpestatus
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
from south.db import db


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_cpestatus",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_periodic_discovery_cpestatus",
            models.BooleanField(default=False)
        )

    def backwards(self):
        pass
