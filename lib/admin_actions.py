# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Commonly used Django admin actions
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

##
## Enable all selected objects
##
def enable_selected(modeladmin,request,queryset):
    objects=list(queryset)
    if hasattr(objects[0],"enabled"):
        attr="enabled"
    elif hasattr(objects[0],"is_enabled"):
        attr="is_enabled"
    else:
        modeladmin.message_user(request,"Cannot enable selected objects")
        return
    for o in objects:
        setattr(o,attr,True)
        o.save()
    count=len(objects)
    if count==1:
        modeladmin.message_user(request,"1 object enabled")
    else:
        modeladmin.message_user(request,"%d objects enabled"%count)
enable_selected.short_description="Enable Selected Objects"

##
## Disable all selected objects
##
def disable_selected(modeladmin,request,queryset):
    objects=list(queryset)
    if hasattr(objects[0],"enabled"):
        attr="enabled"
    elif hasattr(objects[0],"is_enabled"):
        attr="is_enabled"
    else:
        modeladmin.message_user(request,"Cannot disable selected objects")
        return
    for o in objects:
        setattr(o,attr,False)
        o.save()
    count=len(objects)
    if count==1:
        modeladmin.message_user(request,"1 object disabled")
    else:
        modeladmin.message_user(request,"%d objects disabled"%count)
disable_selected.short_description="Disable Selected Objects"