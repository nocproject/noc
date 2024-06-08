# ----------------------------------------------------------------------
# Add Allowed Models to workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from bson import ObjectId
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["workflows"]
        bulk = []
        for wid, model_ids in [
            (ObjectId("5fca627e890f55564231e1f5"), ["inv.Sensor"]),
            (ObjectId("606eafb1d179a5da7e340a3f"), ["sa.Service"]),
            (ObjectId("607a7dddff3a857a47600b9b"), ["sla.SLAProbe"]),
            (ObjectId("610bcff0902971a3863306fb"), ["pm.Agent"]),
            (
                ObjectId("5a01d980b6f529000100d37a"),
                [
                    "ip.Address",
                    "ip.Prefix",
                    "ip.VRF",
                    "vc.VLAN",
                    "vc.VPN",
                    "vc.L2Domain",
                    "crm.Subscriber",
                    "crm.Supplier",
                ],
            ),
        ]:
            bulk += [UpdateOne({"_id": wid}, {"$set": {"allowed_models": model_ids}})]
        if bulk:
            coll.bulk_write(bulk)
