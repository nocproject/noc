# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## User Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import ModelApplication
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
##
##
##
class UserApplication(ModelApplication):
    model=User
    model_admin=UserAdmin
    menu="Setup | Users"
    ##
    ## Change password view
    ##
    def view_change_password(self,request,object_id):
        return self.admin.user_change_password(request,object_id)
    view_change_password.url=r"^(\d+)/password/$"
    view_change_password.access=ModelApplication.permit_change