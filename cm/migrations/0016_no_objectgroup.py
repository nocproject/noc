# encoding: utf-8
from south.db import db


class Migration(object):
    def forwards(self):
        # Drop groups and fields
        db.drop_column("cm_objectnotify", "group_id")

    def backwards(self):
        pass
