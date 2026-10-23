# ----------------------------------------------------------------------
# finish tag migration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    TAG_MODELS = ["dns_dnszone", "dns_dnszonerecord"]

    def migrate(self) -> None:
        # Drop old tags
        for m in self.TAG_MODELS:
            self.db.delete_column(m, "tags")
        # Rename new tags
        for m in self.TAG_MODELS:
            self.db.rename_column(m, "tmp_tags", "tags")
        # Create indexes
        for m in self.TAG_MODELS:
            self.db.execute(f'CREATE INDEX x_{m}_tags ON "{m}" USING GIN("tags")')
