# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.cm.models import *

class Migration:
    depends_on=(
        ("sa","0006_default_activator"),
    )
    def forwards(self):
        a_id=db.execute("SELECT id FROM sa_activator LIMIT 1")[0][0]
        for handler_class_name,repo_path,profile_name,scheme,address,port,user,password,super_password,path\
            in db.execute("SELECT handler_class_name,repo_path,profile_name,scheme,address,port,\"user\",password,super_password,remote_path FROM cm_object"):
            if handler_class_name=="config":
                db.execute("INSERT INTO cm_config(repo_path,activator_id,profile_name,scheme,address,port,\"user\",password,super_password,remote_path) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [repo_path,a_id,profile_name,scheme,address,port,user,password,super_password,path])
            elif handler_class_name=="dns":
                db.execute("INSERT INTO cm_dns(repo_path) VALUES(%s)",[repo_path])
            elif handler_class_name=="prefix-list":
                db.execute("INSERT INTO cm_prefixlist(repo_path) VALUES(%s)",[repo_path])
            else:
                raise Exception("Unsupported handler_class_name='%s'"%handler_class_name)
    
    def backwards(self):
        "Write your backwards migration here"
