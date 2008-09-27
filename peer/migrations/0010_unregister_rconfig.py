
from south.db import db
from noc.peer.models import *
from noc.setup.models import Settings

KEYS=[
    ("rconfig.config", "/tmp/rconfig.conf"),
    ("rconfig.mail_server","mail.example.com"),
    ("rconfig.mail_from","from@example.com"),
    ("rconfig.mail_to","to@example.com"),
]

class Migration:
    def forwards(self):
        Settings.migration_backward(KEYS)

    def backwards(self):
        Settings.migration_forward(KEYS)