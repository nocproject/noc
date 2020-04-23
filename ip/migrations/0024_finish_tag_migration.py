# ----------------------------------------------------------------------
# finish tag migration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    TAG_MODELS = ["ip_vrfgroup", "ip_vrf", "ip_prefix", "ip_address", "ip_addressrange"]

    def migrate(self):
        # Drop old tags
        for m in self.TAG_MODELS:
            self.db.delete_column(m, "tags")
        # Rename new tags
        for m in self.TAG_MODELS:
            self.db.rename_column(m, "tmp_tags", "tags")
        # Create indexes
        for m in self.TAG_MODELS:
            self.db.execute('CREATE INDEX x_%s_tags ON "%s" USING GIN("tags")' % (m, m))
