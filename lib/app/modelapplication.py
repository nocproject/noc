# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ModelApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext as _
from django.contrib import admin as django_admin
from django.utils.encoding import smart_unicode
from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec
from django.views.static import serve as serve_static
from django.db.models.fields import CharField
from django.db.models import Q
from django.db import IntegrityError
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
        self.admin.change_form_template = (
            self.get_template_path("change_form.html") +
            ["admin/change_form.html"]
            )
        self.admin.change_list_template = (
            self.get_template_path("change_list.html") +
            ["admin/change_list.html"]
            )
        # Set up permissions
        self.granular_access = hasattr(self.model, "user_objects")
        self.admin.has_change_permission = self.has_change_permission
        self.admin.has_add_permission = self.has_add_permission
        self.admin.has_delete_permission = self.has_delete_permission
        ## Set up row-based access
        self.admin.queryset = self.queryset
        if not self.query_fields:
            self.query_fields = ["%s__%s" % (f.name, self.query_condition)
                                 for f in self.model._meta.fields
                                 if f.unique and isinstance(f, CharField)]

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
        try:
            return self.admin.delete_view(request, object_id,
                                          self.get_context(extra_context))
        except IntegrityError, why:
            self.message_user(request, "Integrity Error: %s" % why)
            return self.response_redirect("..")
    
    @view(url=r"^(\d+)/$", url_name="change", access=HasPerm("change"))
    def view_change(self,request,object_id,extra_context=None):
        """Display change form"""
        return self.admin.change_view(request, object_id,
                                      self.get_context(extra_context))

    ##
    ## Backport from ExtApplication/ExtModelApplication for lookup support
    ##
    ignored_params = ["_dc"]
    page_param = "__page"
    start_param = "__start"
    limit_param = "__limit"
    sort_param = "__sort"
    format_param = "__format"  # List output format
    query_param = "__query"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"

    @view(url="^(?P<path>(?:js|css|img)/[0-9a-zA-Z_/]+\.(?:js|css|png))$",
          url_name="static", access=True)
    def view_static(self, request, path):
        """
        Static file server.
        """
        return serve_static(request, path, document_root=self.document_root)

    @view(method=["GET"], url=r"^lookup/$", access="lookup", api=True)
    def api_lookup(self, request):
        return self.list_data(request, self.instance_to_lookup)
    
    def instance_to_lookup(self, o):
        return {
            "id": o.id,
            "label": unicode(o)
        }

    def get_Q(self, request, query):
        """
        Prepare Q statement for query
        """
        def get_q(f):
            if "__" not in f:
                return "%s__%s" % (f, self.query_condition)
            else:
                return f

        return reduce(lambda x, y: x | Q(get_q(y)), self.query_fields[1:],
                      Q(**{get_q(self.query_fields[0]): query}))

    def l_queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        if query and self.query_fields:
            return self.model.objects.filter(self.get_Q(request, query))
        else:
            return self.model.objects.all()

    def list_data(self, request, formatter):
        """
        Returns a list of requested object objects
        """
        q = dict(request.GET.items())
        limit = q.get(self.limit_param)
        page = q.get(self.page_param)
        start = q.get(self.start_param)
        format = q.get(self.format_param)
        query = q.get(self.query_param)
        ordering = []
        if format == "ext" and self.sort_param in q:
            for r in self.deserialize(q[self.sort_param]):
                if r["direction"] == "DESC":
                    ordering += ["-%s" % r["property"]]
                else:
                    ordering += [r["property"]]
        q = self.cleaned_query(q)
        if None in q:
            ew = q.pop(None)
            data = self.l_queryset(request, query).filter(**q).extra(where=ew)
        else:
            data = self.l_queryset(request, query).filter(**q)
        # Apply sorting
        if ordering:
            data = data.order_by(*ordering)
        if format == "ext":
            total = data.count()
        if start is not None and limit is not None:
            data = data[int(start):int(start) + int(limit)]
        out = [formatter(o) for o in data]
        if format == "ext":
            out = {
                "total": total,
                "success": True,
                "data": out
            }
        return out

    def cleaned_query(self, q):
        nq = {}
        for p in q:
            if "__" in p:
                np, lt = p.split("__", 1)
            else:
                np, lt = p, None
            # Skip ignored params
            if np in self.ignored_params or p in (
                self.limit_param, self.page_param, self.start_param,
                self.format_param, self.sort_param, self.query_param):
                continue
            v = q[p]
            # Pass through interface cleaners
            if lt == "referred":
                # Unroll __referred
                app, fn = v.split("__", 1)
                model = self.site.apps[app].model
                extra_where = "\"%s\" IN (SELECT \"%s\" FROM %s)" % (
                    self.model._meta.pk.name,
                    model._meta.get_field_by_name(fn)[0].attname,
                    model._meta.db_table
                )
                if None in nq:
                    nq[None] += [extra_where]
                else:
                    nq[None] = [extra_where]
                continue
            elif lt and hasattr(self, "lookup_%s" % lt):
                # Custom lookup
                getattr(self, "lookup_%s" % lt)(nq, np, v)
                continue
            # Write back
            nq[p] = v
        return nq

    def l_queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        if query and self.query_fields:
            return self.model.objects.filter(self.get_Q(request, query))
        else:
            return self.model.objects.all()


class ExistingChoicesFilterSpec(ChoicesFilterSpec):
    """
    List filter. Show only species present in list
    """
    def choices(self, cl):
        yield {
            "selected"    : self.lookup_val is None,
            "query_string": cl.get_query_string({}, [self.lookup_kwarg]),
            "display"     : _("All")}
        
        used = set(self.field.model.objects.distinct().values_list(self.field.name, flat=True))
        for k, v in self.field.flatchoices:
            if k in used:
                yield {
                    "selected"     : smart_unicode(k) == self.lookup_val,
                    "query_string" : cl.get_query_string({self.lookup_kwarg: k}),
                    "display"      : v
                    }

## Install specific filters to all models
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, "existing_choices_filter", False), ExistingChoicesFilterSpec))
