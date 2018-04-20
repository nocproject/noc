# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Initialize SubInterface.managed_object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Initialize SubInterface.managed_object
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import get_db

class Migration:
    def forwards(self):
        db = get_db()
        # interface oid -> managed object id
        imo = dict((r["_id"], r["managed_object"])
                    for r in db.noc.interfaces.find(
                                    {}, {"id": 1, "managed_object": 1}))
        # Update subinterface managed object id
        c = db.noc.subinterfaces
        for i_oid in imo:
            c.update({"interface": i_oid},
                    {"$set": {"managed_object": imo[i_oid]}})

    def backwards(self):
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
