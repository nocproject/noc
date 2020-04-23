# ---------------------------------------------------------------------
# ippool technologies
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from noc.core.model.fields import TextArrayField

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "ip_ippool", "technologies", TextArrayField("Technologies", default=["IPoE"])
        )
