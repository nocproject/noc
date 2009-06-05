# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Decorator Functions
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib.auth.decorators import user_passes_test,REDIRECT_FIELD_NAME
##
## Decorator for views that checks the user is superuser
##
def superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator=user_passes_test(
        lambda u:u.is_superuser,
        redirect_field_name=redirect_field_name
        )
    if function:
        return actual_decorator(function)
    return actual_decorator
