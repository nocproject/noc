# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
<<<<<<< HEAD
from django.db import models

class Migration:

=======
from noc.main.models import *

class Migration:
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        # Create Any time pattern if not exists
        if db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s",["Any"])[0][0]==0:
            db.execute("INSERT INTO main_timepattern(name,description) values(%s,%s)",["Any","Always match"])
        time_pattern_id=db.execute("SELECT id FROM main_timepattern WHERE name=%s",["Any"])[0][0]
        # Fill contacts
        for user_id,email in db.execute("SELECT  id,email FROM auth_user"):
            # Create UserProfile when necessary
            if db.execute("SELECT COUNT(*) FROM main_userprofile WHERE user_id=%s",[user_id])[0][0]==0:
                db.execute("INSERT INTO main_userprofile(user_id) VALUES(%s)",[user_id])
            # Get profile id
            profile_id=db.execute("SELECT id FROM main_userprofile WHERE user_id=%s",[user_id])[0][0]
            # Fill contacts from email field when not filled yet
            if db.execute("SELECT COUNT(*) FROM main_userprofilecontact WHERE user_profile_id=%s AND notification_method=%s AND time_pattern_id=%s AND params=%s",
                    [profile_id,"mail",time_pattern_id,email])[0][0]==0:
                db.execute("INSERT INTO main_userprofilecontact(user_profile_id,time_pattern_id,notification_method,params) VALUES(%s,%s,%s,%s)",
                    [profile_id,time_pattern_id,"mail",email])
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
