# ----------------------------------------------------------------------
# managedobjectprofile asset discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    d_types = ["asset"]

    def migrate(self) -> None:
        for d in self.d_types:
            self.db.add_column(
                "sa_managedobjectprofile",
                f"enable_{d}_discovery",
                models.BooleanField("", default=False),
            )
            self.db.add_column(
                "sa_managedobjectprofile",
                f"{d}_discovery_min_interval",
                models.IntegerField("", default=600),
            )
            self.db.add_column(
                "sa_managedobjectprofile",
                f"{d}_discovery_max_interval",
                models.IntegerField("", default=86400),
            )
