# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VCFilter Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from noc.vc.models import VCFilter
##
## VCFilter admin
##
class VCFilterAdmin(admin.ModelAdmin):
    list_display=["name","expression"]
    search_fields=["name"]
    actions=["test"]
    ##
    ## Test Selected Time Patterns
    ##
    def test(self,request,queryset):
        return self.app.response_redirect("test/%s/"%",".join([str(p.id) for p in queryset]))
    test.short_description="Test selected VC Filters"
##
## VCFilter application
##
class VCFilterApplication(ModelApplication):
    model=VCFilter
    model_admin=VCFilterAdmin
    menu="Setup | VC Filters"
    ##
    ## Test VC Filter Form
    ##    
    class TestVCFilterForm(ModelApplication.Form):
        vc=forms.IntegerField(label="VC ID")
    ##
    ## Test Selected Time Patterns
    ##
    def view_test(self,request,objects):
        vcf=[get_object_or_404(VCFilter,id=int(x)) for x in objects.split(",")]
        result=[]
        if request.POST:
            form=self.TestVCFilterForm(request.POST)
            if form.is_valid():
                vc=form.cleaned_data["vc"]
                result=[{"vcfilter":f,"result":f.check(vc)} for f in vcf]
        else:
            form=self.TestVCFilterForm()
        return self.render(request,"test.html",{"form":form,"result":result})
    view_test.url=r"^test/(?P<objects>\d+(?:,\d+)*)/$"
    view_test.access=HasPerm("change")

