# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# NOC modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import get_db

class Migration:
    def forwards(self):
        expires = datetime.datetime.now() + datetime.timedelta(days=7)
        c = get_db()["noc.log.sa.failed_scripts"]
<<<<<<< HEAD
        c.update_many({}, {
            "$set": {
                "expires": expires
            }
        })
=======
        c.update({}, {
            "$set": {
                "expires": expires
            }
        }, multi=True)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def backwards(self):
        pass
