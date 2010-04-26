# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObjectSelector Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication
from noc.sa.models import ManagedObjectSelector
##
## ManagedObjectSelector admin
##
class ManagedObjectSelectorAdmin(admin.ModelAdmin):
    list_display=["name","is_enabled"]
    list_filter=["is_enabled"]
    actions=["test_selectors"]
    ##
    ## Test selected seletors
    ##
    def test_selectors(self,request,queryset):
        return self.app.response_redirect("test/%s/"%",".join([str(p.id) for p in queryset]))
    test_selectors.short_description="Test selected Object Selectors"
##
## ManagedObjectSelector application
##
class ManagedObjectSelectorApplication(ModelApplication):
    model=ManagedObjectSelector
    model_admin=ManagedObjectSelectorAdmin
    menu="Setup | Object Selectors"
    ##
    ## Test Selectors
    ##
    def view_test(self,request,objects):
        r=[{"name":q.name,"objects":q.managed_objects}
            for q in[get_object_or_404(ManagedObjectSelector,id=int(x)) for x in objects.split(",")]]
        return self.render(request,"test.html",{"data":r})
    view_test.url=r"^test/(?P<objects>\d+(?:,\d+)*)/$"
    view_test.access=ModelApplication.has_perm("sa.change_managedobjectselector")
