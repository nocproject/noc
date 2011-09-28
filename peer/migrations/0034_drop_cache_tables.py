# encoding: utf-8
from south.db import db

class Migration:
    def forwards(self):
        db.delete_table("peer_prefixlistcache")
        db.delete_table("peer_whoiscache")
        db.delete_table("peer_whoislookup")
        db.delete_table("peer_whoisdatabase")

    def backwards(self):
        pass
