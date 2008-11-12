
from south.db import db
from noc.setup.models import *

KEYS=[
    ("shell.pg_dump","/usr/bin/pg_dump"),
    ("main.backup_dir","/var/spool/backup/noc/"),
]

class Migration:
    def forwards(self):
        Settings.migration_forward(KEYS)

    def backwards(self):
        Settings.migration_backward(KEYS)