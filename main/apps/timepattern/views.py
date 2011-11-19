# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TimePattern Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from noc.main.models import TimePattern,TimePatternTerm
import datetime
##
## TimePattern admin
##
class TimePatternTermForm(forms.ModelForm):
    class Meta:
        model=TimePatternTerm
    def clean_term(self):
        try:
            TimePatternTerm.check_syntax(self.cleaned_data["term"])
        except SyntaxError,why:
            raise forms.ValidationError(why)
        return self.cleaned_data["term"]
    
class TimePatternTermAdmin(admin.TabularInline):
    extra=5
    model=TimePatternTerm
    form=TimePatternTermForm
    
class TimePatternAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]
    inlines=[TimePatternTermAdmin]
    actions=["test"]
    ##
    ## Test Selected Time Patterns
    ##
    def test(self,request,queryset):
        return self.app.response_redirect("test/%s/"%",".join([str(p.id) for p in queryset]))
    test.short_description="Test selected Time Patterns"
##
## Test Time Patterns Form
##    
class TestTimePatternsForm(forms.Form):
    time=forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M:%S"])
##
## TimePattern application
##
class TimePatternApplication(ModelApplication):
    model=TimePattern
    model_admin=TimePatternAdmin
    menu="Setup | Time Patterns"
    icon = "icon_time"
    ##
    ## Test Selected Time Patterns
    ##
    def view_test(self,request,objects):
        tp=[get_object_or_404(TimePattern,id=int(x)) for x in objects.split(",")]
        result=[]
        if request.POST:
            form=TestTimePatternsForm(request.POST)
            if form.is_valid():
                t=form.cleaned_data["time"]
                result=[{"pattern":p,"result":p.match(t)} for p in tp]
        else:
            now=datetime.datetime.now()
            s="%02d.%02d.%04d %02d:%02d:%02d"%(now.day,now.month,now.year,now.hour,now.minute,now.second)
            form=TestTimePatternsForm(initial={"time":s})
        return self.render(request,"test.html",{"form":form,"result":result})
    view_test.url=r"^test/(?P<objects>\d+(?:,\d+)*)/$"
    view_test.access=HasPerm("change")
