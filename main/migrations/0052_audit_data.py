# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Migrate audit trail
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import re
import datetime
## Third-party modules
from south.db import db
## Third-party modules
import pymongo
## NOC modules
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
            lines = s.splitlines()
            last = None
            for l in lines:
                if sep not in l:
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
            bulk = collection.initialize_unordered_bulk_op()
            rc = 0
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
                rc += 1
                bulk.insert(o)
                last_id = a_id
            left -= rc
            logger.info("   ... %d records left", left)
            if rc:
                bulk.execute({"w": 0})
            else:
                break
        db.drop_table("main_audittrail")

    def backwards(self):
        pass