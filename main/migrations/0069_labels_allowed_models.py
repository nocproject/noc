# ----------------------------------------------------------------------
# Move enable label setting to allow_models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.models import LABEL_MODELS


class Migration(BaseMigration):
    depends_on = []

    def migrate(self):
        l_coll = self.mongo_db["labels"]
        bulk = []
        setting_map = {v: k for k, v in LABEL_MODELS.items()}
        unset_s = {k: 1 for k in LABEL_MODELS.values()}
        for ll in l_coll.find():
            allow_models = []
            for ff in setting_map:
                if ff in ll and ll[ff]:
                    allow_models.append(setting_map[ff])
            bulk += [
                UpdateOne(
                    {"_id": ll["_id"]}, {"$set": {"allow_models": allow_models}, "$unset": unset_s}
                ),
            ]
        if bulk:
            l_coll.bulk_write(bulk)
