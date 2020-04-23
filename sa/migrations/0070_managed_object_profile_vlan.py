# ----------------------------------------------------------------------
# managedobjectprofile vlan
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    d_types = ["vlan"]

    def migrate(self):
        for d in self.d_types:
            self.db.add_column(
                "sa_managedobjectprofile",
                "enable_%s_discovery" % d,
                models.BooleanField("", default=False),
            )
            self.db.add_column(
                "sa_managedobjectprofile",
                "%s_discovery_min_interval" % d,
                models.IntegerField("", default=600),
            )
            self.db.add_column(
                "sa_managedobjectprofile",
                "%s_discovery_max_interval" % d,
                models.IntegerField("", default=86400),
            )
