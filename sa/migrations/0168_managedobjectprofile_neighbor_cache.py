# ----------------------------------------------------------------------
# ManagedObject.neighbor_cache_ttl
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
            "neighbor_cache_ttl",
            models.IntegerField("Neighbor Cache TTL", default=0),
        )
