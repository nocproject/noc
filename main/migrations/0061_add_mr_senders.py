# ----------------------------------------------------------------------
# Create default MR for senders
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson

# NOC modules
from noc.core.migration.base import BaseMigration

senders = ["mailsender", "tgsender", "icqsender"]


class Migration(BaseMigration):
    def migrate(self):
        mr_coll = self.mongo_db["messageroutes"]
        for sender in senders:
            mx_id = bson.ObjectId()
            mx_data = {
                "_id": mx_id,
                "name": sender.title(),
                "is_active": True,
                "order": 10,
                "type": "notification",
                "match": [{"header": "To", "op": "==", "value": sender}],
                "transmute": [],
                "action": [
                    {
                        "type": "stream",
                        "stream": sender,
                        "headers": [{"header": "To", "value": sender}],
                    }
                ],
            }
            mr_coll.insert_one(mx_data)
