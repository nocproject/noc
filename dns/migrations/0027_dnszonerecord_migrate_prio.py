# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        for id, content in db.execute("""
            SELECT r.id, r.right
            FROM dns_dnszonerecord r JOIN dns_dnszonerecordtype t ON (r.type_id = t.id)
            WHERE
                t.type IN ('MX', 'SRV')
            """):
            prio, rest = content.split(" ", 1)
            try:
                prio = int(prio)
            except ValueError:
                continue
            db.execute("""
                UPDATE dns_dnszonerecord
                SET
                    priority = %s,
                    "right" = %s
                WHERE id = %s
            """, [prio, rest, id])

    def backwards(self):
        pass
