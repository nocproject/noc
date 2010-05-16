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
from django.shortcuts import get_object_or_404
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
        if not self.admin.has_change_permission(request):
            return self.response_fobidden("Permission denied")
        user=get_object_or_404(self.model,pk=object_id)
        if request.POST:
            form=self.admin.change_password_form(user,request.POST)
            if form.is_valid():
                new_user=form.save()
                self.message_user(request,"Password changed")
                return self.response_redirect("main:user:change",object_id)
        else:
            form=self.admin.change_password_form(user)
        return self.render(request,"change_password.html",{"form":form,"original":user})
    view_change_password.url=r"^(\d+)/password/$"
    view_change_password.access=ModelApplication.permit_change