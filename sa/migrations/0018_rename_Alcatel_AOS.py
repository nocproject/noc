# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='Alcatel.OS62xx' WHERE profile_name='Alcatel.AOS'")

=======
    
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='Alcatel.OS62xx' WHERE profile_name='Alcatel.AOS'")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='Alcatel.AOS' WHERE profile_name='Alcatel.OS62xx'")
