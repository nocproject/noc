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
    def forwards(self):
        i=0
        for user_id,administrative_domain_id,group_id in db.execute("SELECT user_id,administrative_domain_id,group_id FROM sa_useraccess"):
            name="NOC_UA_%d_%d"%(user_id,i)
            db.execute("INSERT INTO sa_managedobjectselector(name,description,filter_administrative_domain_id) VALUES(%s,%s,%s)",
                [name,"Auto created from (%s,%s,%s)"%(user_id,administrative_domain_id,group_id),administrative_domain_id])
            if group_id:
                s_id=db.execute("SELECT id FROM sa_managedobjectselector WHERE name=%s",[name])[0][0]
                db.execute("INSERT INTO sa_managedobjectselector_filter_groups(managedobjectselector_id,objectgroup_id) VALUES(%s,%s)",
                    [s_id,group_id])
            i+=1
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.execute("DELETE FROM sa_managedobjectselector WHERE name LIKE 'NOC_UA_%'")
