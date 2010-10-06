# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Local Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class NOCLocalBackend(ModelBackend):
    def authenticate(self,username=None,password=None,**kwargs):
        try:
            user=User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
