# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.delete_column("dns_dnszonerecord", "type_id")
        db.drop_table("dns_dnszonerecordtype")

    def backwards(self):
        pass
