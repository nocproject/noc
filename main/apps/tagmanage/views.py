# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Tag Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from tagging.models import Tag,TaggedItem
## Display tag items count
def tag_items(t):
    return t.items.count()
tag_items.short_description="Items"
##
## Tag admin
##
class TagAdmin(admin.ModelAdmin):
    list_display=["name",tag_items]
    search_fields=["name"]
    actions=["merge_tags"]
    def merge_tags(self,request,queryset):
        return self.app.response_redirect("merge/%s/"%",".join([str(t.id) for t in queryset]))
    merge_tags.short_description="Merge selected tags"
    
##
## Tag application
##
class TagApplication(ModelApplication):
    model=Tag
    model_admin=TagAdmin
    menu="Setup | Tags"
    ##
    ## Merge Selected Tags
    ##
    class FormMerge(forms.Form):
        name=forms.CharField("Name")
    def view_merge(self,request,objects):
        tags=[get_object_or_404(Tag,id=int(x)) for x in objects.split(",")]
        if request.POST:
            form=self.FormMerge(request.POST)
            if form.is_valid():
                # Merge
                name=form.cleaned_data["name"]
                msg="%d tags are merged into '%s'"%(len(tags),name)
                # Check tag "name" exists
                try:
                    tag=Tag.objects.get(name=name)
                except Tag.DoesNotExist:
                    # Rename first tag
                    tag=tags.pop(0)
                    tag.name=name
                    tag.save()
                # Merge other tags
                for i in TaggedItem.objects.filter(tag__in=tags):
                    Tag.objects.add_tag(i.object,name)
                    i.delete()
                # Remove other tags
                for t in tags:
                    t.delete()
                #
                self.message_user(request,msg)
                return self.response_redirect("main:tagmanage:changelist")
        else:
            form=self.FormMerge()
        return self.render(request,"merge.html",{"tags":tags,"form":form})
    view_merge.url=r"^merge/(?P<objects>\d+(?:,\d+)*)/$"
    view_merge.access=HasPerm("change")
        
