# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# i18n
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        for c in (db.noc.alarmclasses, db.noc.eventclasses):
            bulk = []
            for d in c.find({}):
                text = d["text"]["en"]
                bulk += [
                    UpdateOne(
                        {"_id": d["_id"]},
                        {
                            "$set": {
                                "subject_template": text["subject_template"],
                                "body_template": text["body_template"],
                                "symptoms": text["symptoms"],
                                "probable_causes": text["probable_causes"],
                                "recommended_actions": text["recommended_actions"],
                            },
                            "$unset": {"text": ""},
                        },
                    )
                ]
            if bulk:
                print("Commiting changes to database")
                try:
                    db.noc.fm.uptimes.bulk_write(bulk)
                    print("Database has been synced")
                except BulkWriteError as e:
                    print(("Bulk write error: '%s'", e.details))
                    print("Stopping check")
