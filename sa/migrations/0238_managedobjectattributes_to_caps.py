# ----------------------------------------------------------------------
# Migrate ManagedObject Attributes to CAPS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
import bson
from django.db import connection
from psycopg2.extras import execute_values
import uuid
import orjson

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.inv.capabilities"]
        attrs_cap = {
            "Serial Number": bson.ObjectId(),
            "Boot PROM": bson.ObjectId(),
            "HW version": bson.ObjectId(),
            "Build": bson.ObjectId(),
            "Patch Version": bson.ObjectId(),
        }
        coll.insert_many(
            [
                {
                    "_id": attrs_cap["Boot PROM"],
                    "name": "Chassis | Boot PROM",
                    "uuid": uuid.UUID("83650f04-30cd-45d4-b725-36b4d44277bf"),
                    "description": "Chassis Boot PROM version",
                    "type": "str",
                    "category": bson.ObjectId("632004e260df2c92b1a95759"),
                },
                {
                    "_id": attrs_cap["HW version"],
                    "name": "Chassis | HW Version",
                    "uuid": uuid.UUID("2d58f2c3-5272-45d3-a9cf-a8bac6146d54"),
                    "description": "Chassis Hardware Version",
                    "type": "str",
                    "category": bson.ObjectId("632004e260df2c92b1a95759"),
                },
                {
                    "_id": attrs_cap["Serial Number"],
                    "name": "Chassis | Serial Number",
                    "uuid": uuid.UUID("fb17ebf0-75ca-4302-9aab-7dbd1c1668d4"),
                    "description": "Chassis Serial Number for device",
                    "type": "str",
                    "category": bson.ObjectId("632004e260df2c92b1a95759"),
                },
                {
                    "_id": attrs_cap["Build"],
                    "name": "Software | Build Version",
                    "uuid": uuid.UUID("c1d74702-bf0f-4593-8a63-cf3564215946"),
                    "description": "Software build version",
                    "type": "str",
                    "category": bson.ObjectId("632007eb699ff16e2185dbd9"),
                },
                {
                    "_id": attrs_cap["Patch Version"],
                    "name": "Software | Patch Version",
                    "uuid": uuid.UUID("d78ebbb1-8e78-4b13-9c5a-859972f7462e"),
                    "description": "Software Patch Version",
                    "type": "str",
                    "category": bson.ObjectId("632007eb699ff16e2185dbd9"),
                },
            ]
        )
        mo_caps = defaultdict(list)
        for mo_id, attr_name, attr_value in self.db.execute(
            "SELECT managed_object_id, key, value FROM sa_managedobjectattribute"
        ):
            if attr_name not in attrs_cap:
                continue
            mo_caps[mo_id] += [
                {
                    "capability": str(attrs_cap[attr_name]),
                    "value": attr_value,
                    "source": "caps",
                    "scope": "",
                }
            ]
        caps = []
        for mo_id, data in mo_caps.items():
            caps.append((mo_id, orjson.dumps(data).decode("utf-8")))
        cursor = connection.cursor()
        #                 SET mo.caps = mo.caps || c.caps::jsonb
        execute_values(
            cursor,
            """
                UPDATE sa_managedobject AS mo
                SET caps = mo.caps || c.caps::jsonb
                FROM (VALUES %s) AS c(moid, caps)
                WHERE c.moid = mo.id
            """,
            caps,
            page_size=1000,
        )
