# encoding: utf-8
from south.db import db

class Migration:
    depends_on = [
        ("sa", "0077_drop_repo_path")
    ]

    def forwards(self):
        db.drop_table("cm_config")

    def backwards(self):
        pass
