# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM sa_managedobject WHERE name=%s",["ROOT"])[0][0]==0:
            administrative_domain_id=db.execute("SELECT id FROM sa_administrativedomain ORDER BY id")[0][0]
            activator_id=db.execute("SELECT id FROM sa_activator ORDER BY id")[0][0]
            db.execute("""INSERT INTO sa_managedobject(name,is_managed,administrative_domain_id,activator_id,profile_name,scheme,
                        address,is_configuration_managed)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",["ROOT",True,administrative_domain_id,activator_id,"NOC",1,"0.0.0.0",False]
            )
    
    def backwards(self):
        "Write your backwards migration here"
