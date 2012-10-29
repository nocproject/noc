# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.execute("""
        UPDATE dns_dnszonerecord r
        SET
            type = (
                SELECT type
                FROM dns_dnszonerecordtype
                WHERE
                    id = r.type_id
            )
        """)

    def backwards(self):
        pass
