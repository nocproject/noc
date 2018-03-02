# encoding: utf-8
from south.db import db


class Migration:
    def forwards(self):
        db.delete_table("kb_kbentrytemplate_categories")
        db.delete_table("kb_kbentry_categories")
        db.delete_table("kb_kbcategory")

    def backwards(self):
        pass
