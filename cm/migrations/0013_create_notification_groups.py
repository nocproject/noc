# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.cm.models import *

class Migration:
    def create_notification_group(self,name,emails):
        db.execute("INSERT INTO main_notificationgroup(name) values(%s)",[name])
        ng_id=db.execute("SELECT id FROM main_notificationgroup WHERE name=%s",[name])[0][0]
        for m in emails:
            u=db.execute("SELECT id FROM auth_user WHERE email=%s",[m])
            if u:
                user_id=u[0][0]
                db.execute("INSERT INTO main_notificationgroupuser(notification_group_id,time_pattern_id,user_id) VALUES (%s,%s,%s)",
                    [ng_id,self.time_pattern_id,user_id])
            else:
                db.execute("INSERT INTO main_notificationgroupother(notification_group_id,time_pattern_id,notification_method,params) VALUES (%s,%s,%s,%s)",
                    [ng_id,self.time_pattern_id,"mail",m])                
        return ng_id
        
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s",["Any"])[0][0]==0:
            db.execute("INSERT INTO main_timepattern(name,description) values(%s,%s)",["Any","Always match"])
        self.time_pattern_id=db.execute("SELECT id FROM main_timepattern WHERE name=%s",["Any"])[0][0]
        
        for on_id,on_emails in db.execute("SELECT id,emails FROM cm_objectnotify"):
            emails=[x.strip() for x in on_emails.split()]
            ng_id=self.create_notification_group("cm_autocreated_%d"%on_id,emails)
            db.execute("UPDATE cm_objectnotify SET notification_group_id=%s WHERE id=%s",[ng_id,on_id])
    
    def backwards(self):
        "Write your backwards migration here"
