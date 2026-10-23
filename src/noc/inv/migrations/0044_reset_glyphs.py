# ----------------------------------------------------------------------
# Reset ObjectModel.glyph
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        coll = self.mongo_db["inv.objectmodels"]
        coll.update_many({"glyph": {"$exists": True}}, {"$unset": {"glyph": ""}})
