# -*- coding: utf-8 -*-
from noc.lib.nosql import get_db
from noc.settings import config


class Migration:
    def forwards(self):
        db = get_db()
        if db.noc.pm.db.count() == 0:
            ## Create PMDB
            db.noc.pm.db.insert({
                "name": "default",
                "database": db.name,
                "host": db.connection.host,
                "port": db.connection.port,
                "user": config.get("nosql_database", "user"),
                "password": config.get("nosql_database", "password")
            })
            ## Create PMStorage
            db_id = db.noc.pm.db.find()[0]["_id"]
            db.noc.pm.storage.insert({
                "db": db_id,
                "name": "default",
                "collection": "noc.ts.default",
                "raw_retention": 86400
            })
            ## Create PMProbe
            db.noc.pm.probe.insert({
                "name": "default",
                "is_active": True
            })

    def backwards(self):
        pass