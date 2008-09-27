
from south.db import db
from noc.dns.models import *

KEYS=[
    ("dns.zone_cache",  "/tmp/zones/"),
    ("dns.rsync_target","user@host:/path/"),
]

class Migration:
    def forwards(self):
        Settings.migration_backward(KEYS)

    def backwards(self):
        Settings.migration_forward(KEYS)

