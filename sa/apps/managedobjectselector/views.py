# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObjectSelector Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
from django import forms
## NOC modules
from noc.lib.app import ModelApplication, HasPerm
from noc.sa.models import ManagedObjectSelector, ManagedObjectSelectorByAttribute

##
## Filter by attributes inline form
##
class ManagedObjectSeletorByAttributeInlineForm(forms.ModelForm):
    class Meta:
        model=ManagedObjectSelectorByAttribute

##
## Filter by attributes inline
##
class ManagedObjectAttributeInline(admin.TabularInline):
    form=ManagedObjectSeletorByAttributeInlineForm
    model=ManagedObjectSelectorByAttribute
    extra=3

##
##
##
class ManagedObjectSelectorForm(forms.ModelForm):
    class Meta:
        model = ManagedObjectSelector
    
    def __init__(self, *args, **kwargs):
        super(ManagedObjectSelectorForm, self).__init__(*args, **kwargs)
        # Prevent recursion
        if self.instance.id:
            f_src = self.fields["sources"]
            f_src.queryset = ManagedObjectSelector.objects.exclude(
                                id__exact=self.instance.id).exclude(
                                id__in=self.instance.sources_set.all())
    

##
## ManagedObjectSelector admin
##
class ManagedObjectSelectorAdmin(admin.ModelAdmin):
    list_display=["name","is_enabled","description"]
    list_filter=["is_enabled"]
    actions=["test_selectors"]
    search_fields=["name"]
    filter_horizontal=["filter_groups","sources"]
    inlines=[ManagedObjectAttributeInline]
    form = ManagedObjectSelectorForm
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
        r=[{"name":q.name,"objects":sorted(q.managed_objects,lambda x,y:cmp(x.name,y.name))}
            for q in[self.get_object_or_404(ManagedObjectSelector,id=int(x)) for x in objects.split(",")]]
        return self.render(request,"test.html",{"data":r})
    view_test.url=r"^test/(?P<objects>\d+(?:,\d+)*)/$"
    view_test.access=HasPerm("change")
