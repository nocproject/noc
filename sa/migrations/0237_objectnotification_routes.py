# ---------------------------------------------------------------------
# Migrate ObjectNotification to Route
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import orjson
import bson
import hashlib
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0066_default_mx_senders")]

    def migrate(self):
        rg_map = {str(rg["_id"]): rg["name"] for rg in self.mongo_db["resourcegroups"].find()}
        route_bulk = []
        cfgroute_bulk = []
        for condition, message_type in [
            ("config_changed", "config_changed"),
            ("new", "object_new"),
            ("deleted", "object_deleted"),
            ("version_changed", "version_changed"),
            ("config_policy_violation", "config_policy_violation"),
        ]:
            for rg, ng_id in self.db.execute(
                f"SELECT resource_group, notification_group_id FROM sa_objectnotification WHERE {condition} = TRUE"
            ):
                mr_id = bson.ObjectId()
                rg_name = rg_map[rg]
                route = {
                    "_id": mr_id,
                    "name": f"Notification {message_type} for {rg_name}: {ng_id}",
                    "is_active": True,
                    "description": f"Migrate from ObjectNotification for {rg_name}",
                    "order": 10,
                    "type": message_type,
                    "match": [
                        {
                            "labels": [f"noc::resourcegroup::{rg_name}::="],
                            "exclude_labels": [],
                            "administrative_domain": None,
                            "headers_match": [],
                        }
                    ],
                    "action": "notification",
                    "notification_group": ng_id,
                }
                route_bulk += [InsertOne(route)]
                change_id = bson.ObjectId()
                data = orjson.dumps(
                    {
                        "id": str(mr_id),
                        "name": route["name"],
                        "type": route["type"],
                        "order": route["order"],
                        "action": route["action"],
                        "match": [
                            {
                                "labels": [f"noc::resourcegroup::{rg_name}::="],
                                "exclude_labels": [],
                                "administrative_domain": None,
                                "headers": [],
                            }
                        ],
                        "notification_group": str(ng_id),
                        "change_id": str(change_id),
                    }
                )
                cfgroute_bulk += [
                    InsertOne(
                        {
                            "_id": mr_id,
                            "change_id": change_id,
                            "hash": hashlib.sha256(data).hexdigest()[:16],
                            "data": data.decode("utf-8"),
                        }
                    )
                ]
        mr_coll = self.mongo_db["messageroutes"]
        cfg_coll = self.mongo_db["ds_cfgmxroute"]
        if route_bulk:
            mr_coll.bulk_write(route_bulk)
        if cfgroute_bulk:
            cfg_coll.bulk_write(cfgroute_bulk)
