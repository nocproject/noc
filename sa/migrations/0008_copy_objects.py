# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *
import os

class Migration:
    
    def forwards(self):
        def qget(map,key):
            if key is None:
                return None
            return map[key]
        db.start_transaction()
        # Fill administrative domains
        location2domain={}
        for id,name,description in db.execute("SELECT id,name,description FROM cm_objectlocation"):
            db.execute("INSERT INTO sa_administrativedomain(name,description) VALUES(%s,%s)",[name,description])
            location2domain[id]=db.execute("SELECT id FROM sa_administrativedomain WHERE name=%s",[name])[0][0]
        # Fill groups
        category2group={}
        for id,name,description in db.execute("SELECT id,name,description FROM cm_objectcategory"):
            db.execute("INSERT INTO sa_objectgroup(name,description) VALUES(%s,%s)",[name,description])
            category2group[id]=db.execute("SELECT id FROM sa_objectgroup WHERE name=%s",[name])[0][0]
        #
        ManagedObject = db.mock_model(model_name='ManagedObject', db_table='sa_managedobject', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("cm_config","managed_object",models.ForeignKey(ManagedObject,null=True))
        
        # Move objects
        for id,repo_path,activator_id,profile_name,scheme,address,port,user,password,super_password,remote_path,location_id,trap_source_ip,trap_community\
            in db.execute("SELECT id,repo_path,activator_id,profile_name,scheme,address,port,\"user\",password,super_password,remote_path,location_id,trap_source_ip,trap_community FROM cm_config"):
            name=os.path.basename(repo_path)
            db.execute("INSERT INTO sa_managedobject(name,repo_path,activator_id,profile_name,scheme,address,port,\"user\",password,super_password,remote_path,administrative_domain_id,trap_source_ip,trap_community) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            [name,repo_path,activator_id,profile_name,scheme,address,port,user,password,super_password,remote_path,location2domain[location_id],trap_source_ip,trap_community])
            new_id=db.execute("SELECT id FROM sa_managedobject WHERE name=%s",[name])[0][0]
            for object_id,objectcategory_id in db.execute("SELECT object_id,objectcategory_id FROM cm_object_categories WHERE object_id=%s",[id]):
                db.execute("INSERT INTO sa_managedobject_groups(manageobject_id,objectgroup_id) VALUES(%s,%s)",[new_id,category2group[objectcategory_id]])
            db.execute("UPDATE cm_config SET managed_object_id=%s WHERE id=%s",[new_id,id])
        # Move user access
        for category_id,location_id,user_id in db.execute("SELECT category_id,location_id,user_id FROM cm_objectaccess"):
            db.execute("INSERT INTO sa_useraccess(user_id,administrative_domain_id,group_id) VALUES(%s,%s,%s)",[user_id,qget(location2domain,location_id),qget(category2group,category_id)])
        db.execute("ALTER TABLE cm_config ALTER managed_object_id SET NOT NULL")
        
        # Migrate ObjectNotify
        db.add_column("cm_objectnotify","administrative_domain",models.ForeignKey(AdministrativeDomain,verbose_name="Administrative Domain",blank=True,null=True))
        db.add_column("cm_objectnotify","group",models.ForeignKey(ObjectGroup,verbose_name="Group",blank=True,null=True))
        for id,category_id,location_id in db.execute("SELECT id,category_id,location_id FROM cm_objectnotify"):
            db.execute("UPDATE cm_objectnotify SET administrative_domain_id=%s,group_id=%s WHERE id=%s",[qget(location2domain,location_id),qget(category2group,category_id),id])
        db.commit_transaction()
    
    def backwards(self):
        "Write your backwards migration here"
        db.delete_column("cm_config","managed_object_id")
