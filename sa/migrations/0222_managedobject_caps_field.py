# ----------------------------------------------------------------------
# Migrate ManagedObject Caps Field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import orjson
import bson
from collections import defaultdict
import operator
from siphash24 import siphash24

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration

SIPHASH_SEED = b"\x00" * 16


def default(obj):
    if isinstance(obj, bson.ObjectId):
        return str(obj)
    raise TypeError


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobject",
            "caps",
            models.JSONField("Caps Items", null=True, blank=True, default=lambda: "[]"),
        )
        caps_map = {}
        objects_map = defaultdict(set)
        caps_coll = self.mongo_db["noc.sa.objectcapabilities"]
        for caps in caps_coll.find({"caps": {"$exists": True}}):
            if isinstance(caps["_id"], bson.ObjectId):
                # Old migrations is not completed
                continue
            oc = orjson.dumps(
                sorted(caps["caps"], key=operator.itemgetter("capability")),
                default=default,
                option=orjson.OPT_SORT_KEYS,
            )
            c_hash = siphash24(oc, key=SIPHASH_SEED).digest()
            if c_hash not in caps_map:
                caps_map[c_hash] = oc
            objects_map[c_hash].add(caps["_id"])
        for hh in caps_map:
            if not caps_map[hh]:
                continue
            self.db.execute(
                """UPDATE sa_managedobject SET caps = %s::jsonb WHERE id = ANY(%s::int[])""",
                [caps_map[hh].decode("utf-8"), list(objects_map[hh])],
            )
