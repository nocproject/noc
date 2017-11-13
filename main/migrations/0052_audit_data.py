# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Migrate audit trail
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import re
import datetime
# Third-party modules
from south.db import db
from pymongo.errors import BulkWriteError
from pymongo import InsertOne
# NOC modules
from noc.lib.nosql import get_db

logger = logging.getLogger("south")


class Migration:
    rx_field = re.compile("^[a-zA-Z0-9_]+$")

    def forwards(self):
        def q(s):
            if s is None:
                return None
            s = s.strip()
            if not s or s == "None":
                return None
            if s and s.startswith("'") and s.endswith("'"):
                return s[1:-1]
            else:
                return s

        def iteritems(s, sep):
            last = None
            for l in s.splitlines():
                if sep not in l:
                    if last is not None:
                        last += "\n" + l
                elif last:
                    k = l.split(sep)[0]
                    if self.rx_field.match(k):
                        yield last.split(sep, 1)
                        last = l
                    else:
                        last += "\n" + l
                else:
                    last = l
            if last:
                yield last.split(sep, 1)

        delta = datetime.timedelta(days=5 * 365)
        user_cache = dict(db.execute("SELECT id, username FROM auth_user"))
        collection = get_db()["noc.audittrail"]
        left = db.execute("SELECT COUNT(*) FROM main_audittrail")[0][0]
        logger.info("Migration audit trail")
        last_id = 0
        while True:
            bulk = []
            for a_id, user_id, timestamp, model, db_table, op, subject, body in db.execute(
                """
                  SELECT id, user_id, "timestamp", model, db_table,
                      operation, subject, body
                  FROM main_audittrail
                  WHERE id > %s
                  ORDER BY id
                  LIMIT 1000
                """, [last_id]
            ):
                o = {
                    "timestamp": timestamp,
                    "user": user_cache[user_id],
                    "model_id": "%s.%s" % (db_table.split("_")[0], model),
                    "op": op,
                    "expires": timestamp + delta
                }
                changes = []
                if op == "C":
                    # Parse create operation
                    for k, v in iteritems(body, " = "):
                        if k == "id":
                            continue
                        changes += [{
                            "field": k,
                            "old": None,
                            "new": q(v)
                        }]
                elif op == "M":
                    # Parse modify operation
                    for k, v in iteritems(body, ": "):
                        if k == "id":
                            o["id"] = q(v)
                            continue
                        X = v.split(" -> ", 1)
                        if len(X) == 1:
                            x, y = X[0], None
                        else:
                            x, y = X
                        changes += [{
                            "field": k,
                            "old": q(x),
                            "new": q(y)
                        }]
                elif op == "D":
                    # Parse delete operation
                    for k, v in iteritems(body, " = "):
                        if k == "id":
                            o["id"] = q(v)
                            continue
                        changes += [{
                            "field": k,
                            "old": None,
                            "new": v
                        }]
                else:
                    raise ValueError("Invalid op '%s'" % op)
                o["changes"] = changes
                bulk += [InsertOne(o)]
                last_id = a_id
            left -= len(bulk)
            logger.info("   ... %d records left", left)
            if bulk:
                logger.info("Commiting changes to database")
                try:
                    r = collection.bulk_write(bulk)
                    logger.info("Database has been synced")
                    logger.info("Inserted: %d, Modify: %d, Deleted: %d",
                                r.inserted_count + r.upserted_count,
                                r.modified_count, r.deleted_count)
                except BulkWriteError as e:
                    logger.error("Bulk write error: '%s'", e.details)
                    logger.error("Stopping check")
                    break
            else:
                break
        db.drop_table("main_audittrail")

    def backwards(self):
        pass
