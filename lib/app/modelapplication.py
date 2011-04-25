# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ModelApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin as django_admin
from django.contrib import admin
## NOC modules
from access import HasPerm
from application import Application, view
from noc.lib.widgets import tags_list


class ModelApplication(Application):
    """
    Django's ModelAdmin application wrapper
    """
    model = None        # subclass of Model
    model_admin = None  # subclass of ModelAdmin
    menu = None         # Menu Title
    
    def __init__(self, site):
        super(ModelApplication,self).__init__(site)
        ## Check the model has tags and add "tags" column
        try:
            self.model.tags
            self.has_tags = True
        except:
            self.has_tags = False
        if self.has_tags:
            self.model_admin.list_display += [self.display_tags]
        #
        self.admin = self.model_admin(self.model, django_admin.site)
        self.admin.app = self
        self.title = self.model._meta.verbose_name_plural
        # Set up template paths
        self.admin.change_form_template = self.get_template_path("change_form.html")+["admin/change_form.html"]
        self.admin.change_list_template = self.get_template_path("change_list.html")+["admin/change_list.html"]
        # Set up permissions
        self.granular_access = hasattr(self.model, "user_objects")
        self.admin.has_change_permission = self.has_change_permission
        self.admin.has_add_permission = self.has_add_permission
        self.admin.has_delete_permission = self.has_delete_permission
        ## Set up row-based access
        self.admin.queryset = self.queryset
    
    def display_tags(self, o):
        """Render neat tags list"""
        return tags_list(o)
    display_tags.short_description="Tags"
    display_tags.allow_tags=True
    
    def queryset(self, request):
        if self.granular_access:
            return self.model.user_objects(request.user)
        else:
            return self.model.objects
    
    def has_change_permission(self, request, obj=None):
        r=self.view_changelist.access.check(self,request.user,obj)
        if r and obj and self.granular_access:
            return self.queryset(request).filter(id=obj.id).exists()  # Check obj in queryset
        return r
    
    def has_add_permission(self, request):
        return self.view_add.access.check(self, request.user)
    
    def has_delete_permission(self, request, obj=None):
        r=self.view_delete.access.check(self,request.user,obj)
        if r and obj and self.granular_access:
            return self.queryset(request).filter(id=obj.id).exists()  # Check obj in queryset
        return r
    
    def user_access_list(self, user):
        if hasattr(self.model, "user_access_list"):
            return self.model.user_access_list(user)
        else:
            return []

    def group_access_list(self, group):
        if hasattr(self.model, "group_access_list"):
            return self.model.group_access_list(group)
        else:
            return []
    
    def user_access_change_url(self,user):
        if hasattr(self.model, "user_access_change_url"):
            return self.model.user_access_change_url(user)
        else:
            return None
    
    def group_access_change_url(self, group):
        if hasattr(self.model, "group_access_change_url"):
            return self.model.group_access_change_url(group)
        else:
            return []
    
    def get_menu(self):
        """Get menu item name for application"""
        return self.menu
    
    def get_context(self, extra_context):
        """
        Populate template context with additional variables
        """
        if extra_context is None:
            extra_context = {}
        extra_context["app"] = self
        return extra_context
    
    def content_type(self):
        """Model's content type"""
        return "%s.%s" % (self.model._meta.app_label, 
                          self.model._meta.object_name.lower())
    
    @view(url=r"^$", url_name="changelist", access=HasPerm("change"),
          menu=get_menu)
    def view_changelist(self, request, extra_context=None):
        """Display changelist"""
        return self.admin.changelist_view(request,
                                          self.get_context(extra_context))
    
    @view(url=r"^add/$", url_name="add", access=HasPerm("add"))
    def view_add(self, request, form_url="", extra_context=None):
        """Display add form"""
        return self.admin.add_view(request,
                               extra_context=self.get_context(extra_context))
    
    @view(url=r"^(\d+)/history/$", url_name="history",
          access=HasPerm("change"))
    def view_history(self,request,object_id,extra_context=None):
        """Display object's history"""
        return self.admin.history_view(request, object_id, extra_context)
    
    @view(url=r"^(\d+)/delete/$", url_name="delete", access=HasPerm("delete"))
    def view_delete(self, request, object_id, extra_context=None):
        """Delete object"""
        return self.admin.delete_view(request, object_id,
                                      self.get_context(extra_context))
    
    @view(url=r"^(\d+)/$", url_name="change", access=HasPerm("change"))
    def view_change(self,request,object_id,extra_context=None):
        """Display change form"""
        return self.admin.change_view(request, object_id,
                                      self.get_context(extra_context))
    

