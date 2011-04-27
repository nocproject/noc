# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import pprint
import os
import urllib
## Django modules
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
from django.contrib import admin
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.utils.safestring import SafeString
from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec
from django.template import loader
## NOC modules
from noc.lib.app import ModelApplication, site, Permit, PermitSuperuser,\
                        HasPerm, PermissionDenied, view
from noc.sa.models import *
from noc.settings import config
from noc.lib.fileutils import in_dir
##
## Validating form for managed object
##
class ManagedObjectAdminForm(forms.ModelForm):
    class Meta:
        model = ManagedObject
    
    def clean_scheme(self):
        if "profile_name" not in self.cleaned_data:
            return self.cleaned_data["scheme"]
        profile = profile_registry[self.cleaned_data["profile_name"]]
        if self.cleaned_data["scheme"] not in profile.supported_schemes:
            raise forms.ValidationError("Selected scheme is not supported for profile '%s'" % self.cleaned_data["profile_name"])
        return self.cleaned_data["scheme"]
    
    # Check repo_path remains inside repo
    def clean_repo_path(self):
        repo = os.path.join(config.get("cm", "repo"), "config")
        if (self.cleaned_data["repo_path"]
                and self.cleaned_data["repo_path"].startswith(".")):
            raise forms.ValidationError("Invalid repo path")
        if (not in_dir(os.path.join(repo, self.cleaned_data["repo_path"]), repo)
                or self.cleaned_data["repo_path"].startswith(os.sep)):
            raise forms.ValidationError("Repo path must be relative path inside repo")
        return os.path.normpath(self.cleaned_data["repo_path"])
    

##
## Display managed object's actions
##
def action_links(obj):
    r = []
    try:
        r += [("Config", "cm:config:view", [obj.config.id])]
    except:
        pass
    try:
        obj.profile
        r += [("Scripts", "sa:managedobject:scripts", [obj.id])]
    except:
        pass
    r += [("Addresses", "sa:managedobject:addresses", [obj.id])]
    r += [("Attributes", "sa:managedobject:attributes", [obj.id])]
    s = (["<select onchange='document.location=this.options[this.selectedIndex].value;'>",
          "<option>---</option>"] +
        ["<option value='%s'>%s</option>" % (site.reverse(view, *params), title) for title, view, params in r] +
        ["</select>"])
    return "".join(s)
action_links.short_description = "Actions"
action_links.allow_tags = True

##
## Display profile and platform
##
def profile(obj):
    r = ["<a href='?profile_name__exact=%s'>%s</a>" % (obj.profile_name, obj.profile_name)]
    p = " ".join([x for x in [obj.get_attr("vendor"), obj.get_attr("platform")] if x])
    if p:
        r += [p]
    return "<br/>".join(r)
profile.short_description = SafeString("Profile<br/>Platform")
profile.allow_tags = True

##
## Display object status
##
def object_status(o):
    s = []
    if o.is_managed:
        try:
            o.profile
            s += ["<a href='%d/scripts/'><img src='/static/img/managed.png' title='Is Managed' /></a>" % o.id]
        except:
            s += ["<img src='/static/img/managed.png' title='Is Managed' />"]
    if o.is_configuration_managed:
        try:
            s += ["<a href='/cm/config/%d/'><img src='/static/img/configuration.png' title='Configuration Managed' /></a>" % o.config.id]
        except:
            s += ["<img src='/static/img/configuration.png' title='Configuration Managed' />"]

    return " ".join(s)
object_status.short_description = u"Status"
object_status.allow_tags = True

##
## Profile filter
##
class ExistingChoicesFilterSpec(ChoicesFilterSpec):
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
                    "display"      : v}
    

FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, "existing_choices_filter", False), ExistingChoicesFilterSpec))
##
## Administrative domain/activator
##
def domain_activator(o):
    return u"%s/<br/>%s" % (o.administrative_domain.name, o.activator.name)
domain_activator.short_description = SafeString("Adm. Domain/<br/>Activator")
domain_activator.allow_tags = True
##
## Generic returning safe headers
##
def safe_header(name, header):
    f = lambda o: getattr(o, name)
    f.short_description = SafeString(header)
    return f

##
## Reduce task for script results
##
class TaskFailed(object):
    def __init__(self, msg):
        self.msg = u"Task failed: %s" % msg
    
def script_reduce(task):
    from noc.sa.apps.managedobject.views import TaskFailed
    mt = task.maptask_set.all()[0]
    if mt.status != "C":
        msg = str(mt.script_result["text"]) if mt.script_result else ""
        return mt.script_params, TaskFailed(msg)
    return mt.script_params, mt.script_result

##
## Attributes inline form
##
class ManagedObjectAttributeInlineForm(forms.ModelForm):
    class Meta:
        model = ManagedObjectAttribute
    
##
## Attributes inline
##
class ManagedObjectAttributeInline(admin.TabularInline):
    form = ManagedObjectAttributeInlineForm
    model = ManagedObjectAttribute
    extra = 3

##
## ManagedObject admin
##
class ManagedObjectAdmin(admin.ModelAdmin):
    form = ManagedObjectAdminForm
    inlines = [ManagedObjectAttributeInline]
    fieldsets = (
        (None, {
            "fields": ("name", "is_managed", "administrative_domain",
                       "activator", "profile_name", "description")
        }),
        ("Access", {
            "fields": ("scheme", "address", "port", "remote_path")
        }),
        ("Credentials", {
            "fields": ("user", "password", "super_password")
        }),
        ("SNMP", {
            "fields": ("snmp_ro", "snmp_rw", "trap_source_ip", "trap_community")
        }),
        ("CM", {
            "fields": ("is_configuration_managed", "repo_path")
        }),
        ("Rules", {
            "fields": ("config_filter_rule", "config_diff_filter_rule",
                       "config_validation_rule")
        }),
        ("Other", {
            "fields": ("max_scripts", )
        }),
        ("Tags", {
            "fields": ("tags",)
        }),
    )
    list_display = ["name", object_status, profile, "address",
                    domain_activator,
                    "description", "repo_path", action_links]
    list_filter = ["is_managed", "is_configuration_managed", 
                   "activator__shard", "activator",
                   "administrative_domain", "profile_name"]
    search_fields = ["name", "address", "repo_path", "description"]
    object_class = ManagedObject
    actions = ["test_access"]
    ##
    ## Dirty hack to display PasswordInput in admin form
    ##
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ("password", "super_password"):
            kwargs["widget"] = forms.widgets.PasswordInput(render_value=True)
            if "request" in kwargs:  # For Django 1.1 and later compatibility
                kwargs.pop("request", None)
            return db_field.formfield(**kwargs)
        return super(ManagedObjectAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    ##
    ## Row-level access control
    ##
    def has_change_permission(self, request, obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_change_permission(self, request)
    
    def has_delete_permission(self, request, obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_delete_permission(self, request)
    
    def save_model(self, request, obj, form, change):
        # Save before checking
        admin.ModelAdmin.save_model(self, request, obj, form, change)
        # Then check
        if not obj.has_access(request.user):
            raise PermissionDenied()
    
    ##
    ## Test object access
    ##
    def test_access(self, request, queryset):
        return self.app.response_redirect("test/%s/" % ",".join([str(p.id) for p in queryset]))
    test_access.short_description = "Test selected object access"

##
## ManagedObject application
##
class ManagedObjectApplication(ModelApplication):
    model = ManagedObject
    model_admin = ManagedObjectAdmin
    menu = "Managed Objects"
    
    @view(url=r"^(?P<object_id>\d+)/scripts/$",
         url_name="scripts", access=HasPerm("change"))
    def view_scripts(self, request, object_id):
        """
        Render scripts index
        """
        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        p = o.profile_name
        profile = profile_registry[p]
        has_html = lambda s: bool(profile.scripts[s].get_template())
        scripts = sorted([("%s.%s" % (p, x), x, has_html(x))
                          for x in profile.scripts])
        return self.render(request, "scripts.html", object=o, scripts=scripts)
    
    @view(url=r"^(?P<object_id>\d+)/scripts/(?P<script>[^/]+)/(?P<format>RAW|HTML)/$",
          url_name="script", access=HasPerm("change"))
    def view_script(self, request, object_id, script, format):
        """
        Run script
        """
        # Run map/reduce task
        def run_task(**kwargs):
            task = ReduceTask.create_task([o], script_reduce, {}, script, kwargs, None)
            return self.response_redirect("sa:managedobject:scriptresult",
                                          object_id, script, task.id, format)
        #
        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        # Check user has access to object
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        # Check script exists
        if "." not in script:
            script = "%s.%s" % (o.profile_name, script)
        try:
            scr = script_registry[script]
        except:
            return self.response_not_found("No script found")
        form = None
        result = None
        if scr.implements and scr.implements[0].requires_input():
            # Script requires additional parameters
            if request.POST or request.GET:
                form = scr.implements[0].get_form(request.POST or request.GET)  # @todo: need to combine interfaces
                if form.is_valid():
                    return run_task(**form.cleaned_data)
            else:
                form = scr.implements[0].get_form()
        else:
            # Run scripts without parameters
            return run_task()
        return self.render(request, "script_form.html", object=o,
                           script=script, form=form)
    
    ##
    ## Wait for script completion and show results
    ##
    @view(url=r"^(?P<object_id>\d+)/scripts/(?P<script>[^/]+)/(?P<task_id>\d+)/(?P<format>RAW|HTML)$",
          url_name="scriptresult", access=HasPerm("change"))
    def view_scriptresult(self, request, object_id, script, task_id, format):
        object = self.get_object_or_404(ManagedObject, id=int(object_id))
        task = self.get_object_or_404(ReduceTask, id=int(task_id))
        # Check script exists
        try:
            scr = script_registry[script]
        except:
            return self.response_not_found("Script not found")
        # Wait for task completion
        try:
            params, result = task.get_result(block=False)
        except ReduceTask.NotReady:
            return self.render_wait(request, subject="Script %s" % script,
                                    text="Processing script. Please wait ...")
        # Format result
        display_box = True
        refresh = self.site.reverse("sa:managedobject:script", object.id,
            script, format)
        if isinstance(result, TaskFailed):
            result = result.msg
        elif format == "RAW":
            result = pprint.pformat(result)
        elif format == "HTML":
            # Render template
            display_box = False
            t_path = ["sa", "templates"] + scr.get_template().split("/")
            paths = [os.sep.join(["local"] + t_path), os.sep.join(t_path)]
            if params:
                refresh += "?" + urllib.urlencode(params)
            result = SafeString(loader.render_to_string(paths,
                        {"object": object,
                         "script": script,
                         "params": params,
                         "result": result}).encode("utf8"))
        return self.render(request, "script_result.html", object=object,
                           script=script, result=result, refresh=refresh,
                           display_box = display_box)
    ##
    ## AJAX lookup
    ##
    @view(url=r"^lookup/$", url_name="lookup", access=Permit())
    def view_lookup(self, request):
        def lookup_function(q):
            for m in ManagedObject.objects.filter(name__istartswith=q):
                yield m.name
        return self.lookup(request, lookup_function)
    
    ##
    ## Test managed objects access
    ##
    @view(url=r"^test/(?P<objects>\d+(?:,\d+)*)/$", access=HasPerm("change"))
    def view_test(self, request, objects):
        r = []
        for mo in [ManagedObject.objects.get(id=int(x)) for x in objects.split(",")]:
            r += [{
                  "object" : mo,
                  "users"  : sorted([u.username for u in mo.granted_users]),
                  "groups" : sorted([g.name for g in mo.granted_groups]),
                  }]
        return self.render(request, "test.html", data=r)
    
    ##
    ## Display all managed object's addresses
    ##
    @view(url=r"(?P<object_id>\d+)/addresses/", url_name="addresses",
          access=HasPerm("change"))
    def view_addresses(self, request, object_id):
        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        return self.render(request, "addresses.html",
                           addresses=o.address_set.order_by("address"),
                           object=o)
    
    ##
    ## Display all attributes
    ##
    @view(url=r"(?P<object_id>\d+)/attributes/",
          url_name="attributes", access=HasPerm("change"))
    def view_attributes(self, request, object_id):
        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        return self.render(request, "attributes.html",
           attributes=o.managedobjectattribute_set.order_by("key"), object=o)
    
    ##
    def user_access_list(self, user):
        return [s.selector.name for s in UserAccess.objects.filter(user=user)]
    
    ##
    def user_access_change_url(self, user):
        return self.site.reverse("sa:useraccess:changelist",
                                 QUERY={"user__id__exact": user.id})
    
    ##
    def group_access_list(self, group):
        return [s.selector.name for s in GroupAccess.objects.filter(group=group)]
    
    ##
    def group_access_change_url(self, group):
        return self.site.reverse("sa:groupaccess:changelist",
                                 QUERY={"group__id__exact": group.id})

