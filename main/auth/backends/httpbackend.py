# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HTTP Authentication backend
## Trust REMOTE_USER
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class NOCHTTPBackend(ModelBackend):
    def authenticate(self,remote_user,**kwargs):
        if not remote_user:
            return
        user,created=User.objects.get_or_create(username=remote_user)
        if created:
            # Configure user
            user.is_staff=True
            user.save()
        return user
