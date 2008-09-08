
from south.db import db
from noc.setup.models import *

KEYS=[
    ("tt.url",      "http://example.com/ticket=%(tt)s"),
]

class Migration:
    def forwards(self):
        Settings.migration_forward(KEYS)

    def backwards(self):
        Settings.migration_backward(KEYS)