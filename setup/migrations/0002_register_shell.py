
from south.db import db
from noc.setup.models import *

KEYS=[
    ("shell.ssh",   "/usr/bin/ssh"),
    ("shell.rsync", "/usr/local/bin/rsync"),
]

class Migration:
    def forwards(self):
        Settings.migration_forward(KEYS)
    
    def backwards(self):
        Settings.migration_backward(KEYS)
