# ----------------------------------------------------------------------
# Migrate MessageRoute Settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Dict

# Third-party modules
import bson
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    @staticmethod
    def convert_match(match: List[Dict[str, str]], object_profile_map: Dict[int, str]):
        r = []
        for mm in match:
            xx = {}
            if mm["header"] == "Labels":
                xx["labels"] = [mm["value"]]
            elif mm["header"] == "Administrative-Domain-Id":
                xx["administrative_domain"] = int(mm["value"])
            elif mm["header"] == "Profile-Id" and mm["value"] in object_profile_map:
                if mm["op"] == "==":
                    xx["labels"] = [
                        f"noc::managedobjectprofile::{object_profile_map[int(mm['value'])]}::="
                    ]
                elif mm["op"] == "!=":
                    xx["exclude_labels"] = [
                        f"noc::managedobjectprofile::{object_profile_map[int(mm['value'])]}::="
                    ]
            else:
                xx = {"headers_match": [mm.copy()]}
            if xx:
                r.append(xx)
        return r

    def migrate(self):
        mr_coll = self.mongo_db["messageroutes"]
        bulk = []

        object_profile_map = {}
        for op_id, op_name in self.db.execute("SELECT id,name FROM sa_managedobjectprofile"):
            object_profile_map[op_id] = op_name

        processed = set()
        for num, route in enumerate(mr_coll.aggregate([{"$unwind": "$action"}])):
            name = route["name"]
            match = self.convert_match(route["match"], object_profile_map)
            route_new = {
                "_id": route["_id"],
                "name": name,
                "is_active": route["is_active"],
                "description": route.get("description"),
                "order": route["order"],
                # Message-Type header value
                "type": route["type"],
                # Match message headers
                "match": match,
                # Message actions
                "action": route["action"].get("type"),
                "stream": route["action"].get("stream"),
                "notification_group": route["action"].get("notification_group"),
                "headers": route["action"].get("headers"),
            }
            if "transmute" in route and route["transmute"] and route["transmute"][0].get("handler"):
                route_new["transmute_handler"] = route["transmute"]["handler"]
            if (
                "transmute" in route
                and route["transmute"]
                and route["transmute"][0].get("template")
            ):
                route_new["transmute_template"] = route["transmute"][0]["template"]
            if name in processed:
                route_new["name"] = f"{name}_{num}"
                route_new["_id"] = bson.ObjectId()
            bulk += [InsertOne(route_new)]
            processed.add(name)
        if bulk:
            mr_coll.delete_many({})
            mr_coll.bulk_write(bulk)
