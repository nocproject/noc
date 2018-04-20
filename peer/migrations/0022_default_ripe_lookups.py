# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM peer_whoisdatabase WHERE name=%s", ["RIPE"])[0][0] == 0:
            db.execute("INSERT INTO peer_whoisdatabase(name) VALUES(%s)", ["RIPE"])
        ripe_id = db.execute("SELECT id FROM peer_whoisdatabase WHERE name=%s", ["RIPE"])[0][0]
        for url, direction, key, value in [
            ("ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.as-set.gz", "F", "as-set", "members"),
            ("ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.route.gz", "R", "origin", "route")
        ]:
            db.execute(
                "INSERT INTO peer_whoislookup(whois_database_id,url,direction,key,value) values(%s,%s,%s,%s,%s)",
                [ripe_id, url, direction, key, value])

=======
from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM peer_whoisdatabase WHERE name=%s",["RIPE"])[0][0]==0:
            db.execute("INSERT INTO peer_whoisdatabase(name) VALUES(%s)",["RIPE"])
        ripe_id=db.execute("SELECT id FROM peer_whoisdatabase WHERE name=%s",["RIPE"])[0][0]
        for url,direction,key,value in [
            ("ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.as-set.gz","F","as-set","members"),
            ("ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.route.gz","R","origin","route")]:
            db.execute("INSERT INTO peer_whoislookup(whois_database_id,url,direction,key,value) values(%s,%s,%s,%s,%s)",
                [ripe_id,url,direction,key,value])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
