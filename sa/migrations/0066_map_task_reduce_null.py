# encoding: utf-8
from south.db import db

class Migration:
    def forwards(self):
        db.execute("ALTER TABLE sa_maptask ALTER task_id DROP NOT NULL")

    def backwards(self):
        pass
