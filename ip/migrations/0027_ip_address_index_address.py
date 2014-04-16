# encoding: utf-8
from south.db import db


class Migration:

    def forwards(self):
        db.create_index("ip_address", ["address"], db_tablespace="")

    def backwards(self):
        pass
