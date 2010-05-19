# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventCorrelationRule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.fm.models import EventCorrelationRule,EventCorrelationMatchedClass,EventCorrelationMatchedVar
##
## Inline for matched classes
##
class EventCorrelationMatchedClassAdmin(admin.TabularInline):
    extra=3
    model=EventCorrelationMatchedClass
##
## Inline for matched vars
##
class EventCorrelationMatchedVarAdmin(admin.TabularInline):
    extra=3
    model=EventCorrelationMatchedVar
##
## EventCorrelationRule admin
##
class EventCorrelationRuleAdmin(admin.ModelAdmin):
    list_display=["name","is_builtin"]
    search_fields=["name"]
    list_filter=["is_builtin"]
    inlines=[EventCorrelationMatchedClassAdmin,EventCorrelationMatchedVarAdmin]
    actions=["view_python"]
    ##
    ## Display python code for selected objects
    ##
    def view_python(self,request,queryset):
        code="\n\n".join([o.python_code for o in queryset])
        return self.app.render_plain_text(code)
    view_python.short_description="View Python Code for selected objects"
##
## EventCorrelationRule application
##
class EventCorrelationRuleApplication(ModelApplication):
    model=EventCorrelationRule
    model_admin=EventCorrelationRuleAdmin
    menu="Setup | Correlation Rules"
