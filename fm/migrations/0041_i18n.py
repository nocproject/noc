# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
# NOC modules
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        db = get_db()
        for c in (db.noc.alarmclasses, db.noc.eventclasses):
            bulk = []
            for d in c.find({}):
                text = d["text"]["en"]
                bulk += [UpdateOne({"_id": d["_id"]}, {
                    "$set": {
                        "subject_template": text["subject_template"],
                        "body_template": text["body_template"],
                        "symptoms": text["symptoms"],
                        "probable_causes": text["probable_causes"],
                        "recommended_actions": text["recommended_actions"]
                    },
                    "$unset": {
                        "text": ""
                    }
                })]
            if bulk:
                print("Commiting changes to database")
                try:
                    db.noc.fm.uptimes.bulk_write(bulk)
                    print("Database has been synced")
                except BulkWriteError as e:
                    print("Bulk write error: '%s'", e.details)
                    print("Stopping check")

    def backwards(self):
        pass
