# encoding: utf-8
from south.db import db

class Migration:
    def forwards(self):
        # Drop old tags
        db.drop_column("sa_managedobjectselector", "filter_tags")
        # Rename new tags
        db.rename_column("sa_managedobjectselector",
                         "tmp_filter_tags", "filter_tags")

    def backwards(self):
        pass
