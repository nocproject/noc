# ----------------------------------------------------------------------
# set probe credentials
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0021_permission")]

    def migrate(self):
        PROBEUSER = "noc-probe"
        mdb = self.mongo_db
        # Check probe has no storage and credentials
        if mdb.noc.pm.probe.count_documents({}) != 1:
            return
        p = mdb.noc.pm.probe.find_one({})
        if p.get("storage") or p.get("user"):
            return
        # Check user probe is not exists
        if (
            self.db.execute("SELECT COUNT(*) FROM auth_user WHERE username=%s", [PROBEUSER])[0][0]
            > 0
        ):
            return
        # Check ./noc user is valid command
        if not os.path.exists("main/management/commands/user.py"):
            return
        # Check ./scripts/set-conf.py is exists
        if not os.path.exists("scripts/set-conf.py"):
            return
        # Check probe config is exists
        if not os.path.exists("etc/noc-probe.conf"):
            return
        # Create user and set config
        os.system("./scripts/set-conf.py etc/noc-probe.conf autoconf user %s" % PROBEUSER)
        r = os.system(
            "PW=`./noc user --add --username=%s --email=test@example.com --template=probe --pwgen` &&"
            "./scripts/set-conf.py etc/noc-probe.conf autoconf passwd $PW" % PROBEUSER
        )
        if r != 0:
            import sys

            sys.stderr.write("\nCannot create probe user. Terminating\n")
            sys.exit(1)
        uid = self.db.execute("SELECT id FROM auth_user WHERE username=%s", [PROBEUSER])[0][0]
        sid = mdb.noc.pm.storages.find_one({})["_id"]
        mdb.noc.pm.probe.update_many({}, {"$set": {"storage": sid, "user": uid}})
