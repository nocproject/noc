# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import pprint
import os
import urllib
import datetime
## Django modules
from django.utils.translation import ugettext as _
from django.contrib import admin
from django import forms
from django.utils.safestring import SafeString
from django.template import loader
## NOC modules
from noc.lib.app import (ModelApplication, site, Permit,
                        HasPerm, PermissionDenied, view)
from noc.main.models import CustomField
from noc.sa.models import *
from noc.settings import config
from noc.lib.fileutils import in_dir
from noc.lib.widgets import PasswordWidget
from noc.lib.ip import IP
from noc.fm.models import ActiveAlarm, AlarmSeverity


class ManagedObjectAdminForm(forms.ModelForm):
    """
    Validating form for managed object
    """
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
        path = os.path.join(repo, self.cleaned_data["repo_path"])
        if (self.cleaned_data["repo_path"]
                and self.cleaned_data["repo_path"].startswith(".")):
            raise forms.ValidationError("Invalid repo path")
        if (not in_dir(path, repo)
                or self.cleaned_data["repo_path"].startswith(os.sep)):
            raise forms.ValidationError("Repo path must be relative path inside repo")
        if os.path.isdir(path):
            raise forms.ValidationError(_("Repo path cannot be a directory"))
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


def profile(obj):
    """
    Display profile and platform
    :param obj:
    :return:
    """
    r = ["<a href='?profile_name__exact=%s'>%s</a>" % (obj.profile_name, obj.profile_name)]
    p = " ".join([x for x in [obj.get_attr("vendor"), obj.get_attr("platform")] if x])
    if p:
        r += [p]
    return "<br/>".join(r)
profile.short_description = SafeString("Profile<br/>Platform")
profile.allow_tags = True


def object_status(o):
    """
    Display object status
    :param o:
    :return:
    """
    s = []
    status = o.get_status()
    if status:
        s += ["<img src='/media/admin/img/icon-yes.gif' title='Up' />"]
    else:
        s += ["<img src='/media/admin/img/icon-no.gif' title='Down' />"]
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
object_status.short_description = SafeString(u"&nbsp;&nbsp;Status&nbsp;&nbsp;")
object_status.allow_tags = True


def alarms(o):
    n = ActiveAlarm.objects.filter(managed_object=o.id).count()
    if n:
        return "<a href='%d/alarms/'>%d</a>" % (o.id, n)
    else:
        return "0"
alarms.short_description = u"Alarms"
alarms.allow_tags = True

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
                       "activator", "profile_name", "object_profile",
                       "description", "shape")
        }),
        ("Access", {
            "fields": ("scheme", "address", "port", "remote_path", "vrf")
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
        ("L2", {
            "fields": ("vc_domain", )
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
        ("Custom", {
            "fields": tuple(f.name for f in
                CustomField.table_fields("sa_managedobject"))
        })
    )
    list_display = ["name", object_status, alarms, profile,
                    "object_profile", "vrf", "address", "vc_domain",
                    domain_activator,
                    "description", "repo_path", action_links]
    list_filter = ["is_managed", "is_configuration_managed",
                   "activator__shard", "activator",
                   "administrative_domain", "vrf", "profile_name",
                   "object_profile", "vc_domain"]
    search_fields = ["name", "address", "repo_path", "description"]
    object_class = ManagedObject
    actions = ["test_access", "bulk_change_activator",
               "reschedule_discovery", "apply_config_filters"]
    ##
    ## Dirty hack to display PasswordInput in admin form
    ##
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ("password", "super_password"):
            kwargs["widget"] = PasswordWidget(render_value=True)
            if "request" in kwargs:  # For Django 1.1 and later compatibility
                kwargs.pop("request", None)
            return db_field.formfield(**kwargs)
        return super(ManagedObjectAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)
    
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
            # Will be rolled back by exception handler
            raise PermissionDenied("Permission denied")

    def test_access(self, request, queryset):
        """
        Test access to the objects
        """
        return self.app.response_redirect("test/%s/" % ",".join([str(p.id) for p in queryset]))
    test_access.short_description = _("Test selected object access")

    def bulk_change_activator(self, request, queryset):
        """
        Bulk change activator form
        """
        return self.app.response_redirect("sa:managedobject:change_activator",
                                    ",".join([str(p.id) for p in queryset]))
    bulk_change_activator.short_description = _("Change activator for selected objects")

    def reschedule_discovery(self, request, queryset):
        """
        Reschedule interface discovery
        """
        self.app.message_user(request, "Interface discovery has been rescheduled")
        for o in queryset:
            o.run_discovery()
        return self.app.response_redirect("sa:managedobject:changelist")
    reschedule_discovery.short_description = _("Run discovery now")

    def apply_config_filters(self, request, queryset):
        """
        Apply config filter pyRule
        """
        self.app.message_user(request, "Config filters are reapplied")
        for o in queryset.filter(config__isnull=False):
            cfg = o.config.data
            if cfg:
                o.config.write(cfg)
        return self.app.response_redirect("sa:managedobject:changelist")
    apply_config_filters.short_description = _("Apply Config Filters")

##
## ManagedObject application
##
class ManagedObjectApplication(ModelApplication):
    model = ManagedObject
    model_admin = ManagedObjectAdmin
    menu = "Managed Objects"
    query_condition = "icontains"

    @view(url=r"^(\d+)/delete/$", url_name="delete", access="delete")
    def view_delete(self, request, object_id, extra_context=None):
        """Delete object"""
        self.message_user(request,
            "Use './noc wipe managed_object %d' to wipe managed object" % int(object_id))
        return self.response_redirect_to_referrer(request)

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
                           display_box=display_box)

    ##
    ## AJAX lookup
    ##
    @view(url=r"^lookup1/$", url_name="lookup1", access=Permit())
    def view_lookup1(self, request):
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
                  "object": mo,
                  "users": sorted([u.username for u in mo.granted_users]),
                  "groups": sorted([g.name for g in mo.granted_groups]),
                  }]
        return self.render(request, "test.html", data=r)

    class ChangeActivatorForm(forms.Form):
        activator = forms.ModelChoiceField(label=_("New activator"),
            queryset=Activator.objects.filter(is_active=True).order_by("name"))

    @view(url=r"^change/activator/(?P<objects>\d+(?:,\d+)*)/$",
          url_name="change_activator", access=HasPerm("change"))
    def view_change_activator(self, request, objects):
        """
        Change activator for selected objects
        """
        user = request.user
        o_list = [ManagedObject.objects.get(id=int(x))
                  for x in objects.split(",")]
        o_list = [o for o in o_list if o.has_access(user)]
        if request.POST:
            form = self.ChangeActivatorForm(request.POST)
            if form.is_valid():
                n = 0
                activator = form.cleaned_data["activator"]
                for o in o_list:
                    o.activator = activator
                    o.save()
                    n += 1
                self.message_user(request,
                                  _("Activators for %(numobjects)d have been changed" % {"numobjects": n}))
                return self.response_redirect("sa:managedobject:changelist")
        else:
            form = self.ChangeActivatorForm()
        return self.render(request, "change_activator.html", objects=o_list,
                           form=form)

    ##
    ## Display all managed object's addresses
    ##
    @view(url=r"(?P<object_id>\d+)/addresses/", url_name="addresses",
          access=HasPerm("change"))
    def view_addresses(self, request, object_id):
        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        # Group by parents
        r = {}
        for a in o.address_set.all():
            p = a.prefix
            try:
                r[p] += [a]
            except KeyError:
                r[p] = [a]
        # Order result
        rr = [(p, sorted(r[p], key=lambda x: IP.prefix(x.address)))
              for p in sorted(r, key=lambda x: IP.prefix(x.prefix))]
        return self.render(request, "addresses.html",
                           data=rr,
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

    @view(url=r"(?P<object_id>\d+)/alarms/", url_name="active_alarms",
          access=HasPerm("change"))
    def view_alarms(self, request, object_id):
        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        u_lang = request.session["django_language"]
        alarms = [(a, AlarmSeverity.get_severity(a.severity), a.get_translated_subject(u_lang))
            for a in
            ActiveAlarm.objects.filter(managed_object=o.id).order_by("-severity,timestamp")]
        return self.render(request, "alarms.html",
                           object=o, alarms=alarms)
    
    def user_access_list(self, user):
        return [s.selector.name for s in UserAccess.objects.filter(user=user)]
    
    def user_access_change_url(self, user):
        return self.site.reverse("sa:useraccess:changelist",
                                 QUERY={"user__id__exact": user.id})
    
    def group_access_list(self, group):
        return [s.selector.name for s in GroupAccess.objects.filter(group=group)]
    
    def group_access_change_url(self, group):
        return "/sa/groupaccess/"
        # return self.site.reverse("sa:groupaccess:changelist",
        #                         QUERY={"group__id__exact": group.id})
