# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Default stomp users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Default stomp users
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

from noc.lib.nosql import get_db

class Migration:
    def forwards(self):
        s = get_db().noc.stomp_access
        if not s.count():
            s.insert({"user": "noc", "password": "noc", "is_active": True})

    def backwards(self):
        pass
