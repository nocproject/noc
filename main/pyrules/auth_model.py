# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Returns authentication form class for user/password validation
##----------------------------------------------------------------------
## INTERFACE: IAuthenticationBackend
##----------------------------------------------------------------------
## DESCRIPTION:
## Example authentication backend for model authentication
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib.auth.models import User

@pyrule
def authenticate(username=None,password=None,**kwargs):
    try:
        user=User.objects.get(username=username)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        return None

