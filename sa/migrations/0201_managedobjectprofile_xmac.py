# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectProfile.object_validation_policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_xmac",
            models.BooleanField(default=False),
        )
