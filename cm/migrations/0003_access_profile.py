# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.cm.models import *
from noc.lib.url import URL

class Migration:
    
    def forwards(self):
        db.add_column("cm_object","scheme",models.IntegerField("Scheme",blank=True,null=True,choices=[(0,"telnet"),(1,"ssh")]))
        db.add_column("cm_object","address",models.CharField("Address",max_length=64,blank=True,null=True))
        db.add_column("cm_object","port",models.PositiveIntegerField("Port",blank=True,null=True))
        db.add_column("cm_object","user",models.CharField("User",max_length=32,blank=True,null=True))
        db.add_column("cm_object","password",models.CharField("Password",max_length=32,blank=True,null=True))
        db.add_column("cm_object","super_password",models.CharField("Super Password",max_length=32,blank=True,null=True))
        db.add_column("cm_object","remote_path",models.CharField("Path",max_length=32,blank=True,null=True))
        for id,url in db.execute("SELECT id,stream_url FROM cm_object WHERE stream_url!='ssh://u:p@localhost/'"):
            u=URL(url)
            scheme={"telnet":0,"ssh":1}[u.scheme]
            if u.path=="/":
                u.path=None
            db.execute("UPDATE cm_object SET scheme=%s,address=%s,port=%s,\"user\"=%s,password=%s,remote_path=%s WHERE id=%s",
                [scheme,u.host,u.port,u.user,u.password,u.path,id])
        db.delete_column("cm_object","stream_url")
    
    def backwards(self):
        db.delete_column("cm_object","scheme")
        db.delete_column("cm_object","address")
        db.delete_column("cm_object","port")
        db.delete_column("cm_object","user")
        db.delete_column("cm_object","password")
        db.delete_column("cm_object","super_password")
        db.delete_column("cm_object","remote_path")
