# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.main.models import *

class Migration:
    
    def forwards(self):
        # Create plpgsql language when necessary
        if db.execute("SELECT COUNT(*) FROM pg_language WHERE lanname='plpgsql'")[0][0]==0:
            db.execute("CREATE LANGUAGE plpgsql")
        # Create default admin user if no user exists
        if db.execute("SELECT COUNT(*) FROM auth_user")[0][0]==0:
            db.execute("""
            INSERT INTO auth_user(username,first_name,last_name,email,password,is_staff,is_active,is_superuser,last_login,date_joined)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'now','now')""",
            ["admin","NOC","Admin","test@example.com","sha1$235c1$e8e4d9aaa945e1fae62a965ee87fbf7b4a185e3f",True,True,True])
    
    def backwards(self):
        pass
        
