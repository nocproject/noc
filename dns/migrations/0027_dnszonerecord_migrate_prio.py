# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszonerecord migrate prio
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        for id, content in db.execute("""
                SELECT r.id, r.right
                FROM dns_dnszonerecord r
                JOIN dns_dnszonerecordtype t ON (r.type_id = t.id)
                WHERE t.type IN ('MX', 'SRV') """):
            if " " not in content:
                continue
            prio, rest = content.split(" ", 1)
            try:
                prio = int(prio)
            except ValueError:
                continue
            db.execute(
                """
                UPDATE dns_dnszonerecord
                SET
                    priority = %s,
                    "right" = %s
                WHERE id = %s
            """, [prio, rest, id]
            )

    def backwards(self):
        pass
