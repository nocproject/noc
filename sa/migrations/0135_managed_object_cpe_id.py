# ----------------------------------------------------------------------
# managedobject cpe_id
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
            "sa_managedobject",
            "local_cpe_id",
            models.CharField("Local CPE ID", max_length=128, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "global_cpe_id",
            models.CharField("Global CPE ID", max_length=128, null=True, blank=True),
        )
        self.db.create_index("sa_managedobject", ["local_cpe_id"], unique=False)
        self.db.create_index("sa_managedobject", ["global_cpe_id"], unique=True)
