# ----------------------------------------------------------------------
# Migrate MapSettins to generator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.mongo_db["noc.mapsettings"].drop_index("segment_1")
        self.mongo_db["noc.mapsettings"].aggregate(
            [
                {"$addFields": {"gen_id": "$segment", "gen_type": "segment"}},
                {"$out": "noc.mapsettings"},
            ]
        )
        self.mongo_db["noc.mapsettings"].update_many(
            {"segment": {"$exists": True}}, {"$unset": {"segment": 1}}
        )
