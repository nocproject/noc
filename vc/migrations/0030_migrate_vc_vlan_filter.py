# ----------------------------------------------------------------------
# Migrate VC Filter to VLAN Filter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details

# Third-party modules
import bson
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.text import ranges_to_list


class Migration(BaseMigration):
    def migrate(self):
        bulk = []
        vf_coll = self.mongo_db["vlanfilters"]
        vf_names = {vf["name"] for vf in vf_coll.find()}
        for name, expression, description in self.db.execute(
            "SELECT name, expression, description FROM vc_vcfilter"
        ):
            if name in vf_names:
                continue
            bulk += [
                InsertOne(
                    {
                        "_id": bson.ObjectId(),
                        "name": name,
                        "description": description,
                        "include_expression": expression,
                        "include_vlans": ranges_to_list(expression),
                    }
                )
            ]
        if bulk:
            vf_coll.bulk_write(bulk)
