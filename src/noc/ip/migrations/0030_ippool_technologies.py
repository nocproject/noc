# ---------------------------------------------------------------------
# ippool technologies
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import TextArrayField


class Migration(BaseMigration):
    def migrate(self) -> None:
        self.db.add_column(
            "ip_ippool", "technologies", TextArrayField("Technologies", default=["IPoE"])
        )
