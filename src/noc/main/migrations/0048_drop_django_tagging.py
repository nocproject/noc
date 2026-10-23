# ---------------------------------------------------------------------
# Drop django-tagging tables
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        for t in ["tagging_taggeditem", "tagging_tag"]:
            if self.db.execute(f"SELECT COUNT(*) FROM pg_class WHERE relname='{t}'")[0][0] == 1:
                self.db.delete_table(t)
