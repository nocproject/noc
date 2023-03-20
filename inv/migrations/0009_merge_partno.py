# ---------------------------------------------------------------------
# Initialize inventory hierarchy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        for om in db.noc.objectmodels.find():
            if "data" not in om:
                continue
            if "asset" not in om["data"]:
                continue
            part_no = []
            order_part_no = []
            uso = {}
            so = {}
            for k in om["data"]["asset"]:
                if k.startswith("part_no") and k != "part_no":
                    part_no += [om["data"]["asset"][k]]
                    uso["data.asset.%s" % k] = ""
                elif k.startswith("order_part_no") and k != "order_part_no":
                    order_part_no += [om["data"]["asset"][k]]
                    uso["data.asset.%s" % k] = ""
            if not part_no and not order_part_no:
                continue
            if part_no:
                so["data.asset.part_no"] = part_no
            if order_part_no:
                so["data.asset.order_part_no"] = order_part_no
            db.noc.objectmodels.update_one({"_id": om["_id"]}, {"$set": so, "$unset": uso})
