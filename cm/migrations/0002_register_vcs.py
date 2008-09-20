
from south.db import db
from noc.setup.models import *

KEYS=[
    ("cm.vcs_type","hg"),
    ("cm.vcs_path","/usr/local/bin/hg"),
    ("cm.repo","/tmp/repo"),
]

class Migration:
    def forwards(self):
        Settings.migration_forward(KEYS)

    def backwards(self):
        Settings.migration_backward(KEYS)