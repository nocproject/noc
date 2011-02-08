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
## Django modules
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.utils.safestring import SafeString
## NOC modules
from noc.lib.app import ModelApplication, site, Permit, PermitSuperuser, HasPerm, PermissionDenied, view
from noc.sa.models import *
from noc.settings import config
from noc.lib.fileutils import in_dir
##
## Validating form for managed object
##
class ManagedObjectAdminForm(forms.ModelForm):
    class Meta:
        model=ManagedObject
    def clean_scheme(self):
        if "profile_name" not in self.cleaned_data:
            return self.cleaned_data["scheme"]
        profile=profile_registry[self.cleaned_data["profile_name"]]
        if self.cleaned_data["scheme"] not in profile.supported_schemes:
            raise forms.ValidationError("Selected scheme is not supported for profile '%s'"%self.cleaned_data["profile_name"])
        return self.cleaned_data["scheme"]
    # Check repo_path remains inside repo
    def clean_repo_path(self):
        repo=os.path.join(config.get("cm","repo"),"config")
        if self.cleaned_data["repo_path"] and self.cleaned_data["repo_path"].startswith("."):
            raise forms.ValidationError("Invalid repo path")
        if not in_dir(os.path.join(repo,self.cleaned_data["repo_path"]),repo) or self.cleaned_data["repo_path"].startswith(os.sep):
            raise forms.ValidationError("Repo path must be relative path inside repo")
        return os.path.normpath(self.cleaned_data["repo_path"])
##
## Display managed object's actions
##
def action_links(obj):
    r=[]
    try:
        r+=[("Config", "cm:config:view", [obj.config.id])]
    except:
        pass
    try:
        obj.profile
        r+=[("Scripts", "sa:managedobject:scripts", [obj.id])]
    except:
        pass
    r+=[("Addresses", "sa:managedobject:addresses", [obj.id])]
    r+=[("Attributes", "sa:managedobject:attributes", [obj.id])]
    s=["<select onchange='document.location=this.options[this.selectedIndex].value;'>","<option>---</option>"]+["<option value='%s'>%s</option>"%(site.reverse(view,*params),title) for title, view, params in r]+["</select>"]
    return "".join(s)
action_links.short_description="Actions"
action_links.allow_tags=True

##
## Display object status
##
def object_status(o):
    s=[]
    if o.is_managed:
        try:
            o.profile
            s+=["<a href='%d/scripts/'><img src='/static/img/managed.png' title='Is Managed' /></a>"%o.id]
        except:
            s+=["<img src='/static/img/managed.png' title='Is Managed' />"]
    if o.is_configuration_managed:
        try:
            s+=["<a href='/cm/config/%d/'><img src='/static/img/configuration.png' title='Configuration Managed' /></a>"%o.config.id]
        except:
            s+=["<img src='/static/img/configuration.png' title='Configuration Managed' />"]

    return " ".join(s)
object_status.short_description=u"Status"
object_status.allow_tags=True

##
## Administrative domain/activator
##
def domain_activator(o):
    return u"%s/<br/>%s"%(o.administrative_domain.name, o.activator.name)
domain_activator.short_description=SafeString("Adm. Domain/<br/>Activator")
domain_activator.allow_tags=True
##
## Generic returning safe headers
##
def safe_header(name, header):
    f=lambda o: getattr(o, name)
    f.short_description=SafeString(header)
    return f

##
## Reduce task for script results
##
def script_reduce(task):
    mt=task.maptask_set.all()[0]
    if mt.status!="C":
        return "Task failed: "+(str(mt.script_result["text"]) if mt.script_result else "")
    return mt.script_result

##
## Attributes inline form
##
class ManagedObjectAttributeInlineForm(forms.ModelForm):
    class Meta:
        model=ManagedObjectAttribute
    
##
## Attributes inline
##
class ManagedObjectAttributeInline(admin.TabularInline):
    form=ManagedObjectAttributeInlineForm
    model=ManagedObjectAttribute
    extra=3

##
## ManagedObject admin
##
class ManagedObjectAdmin(admin.ModelAdmin):
    form=ManagedObjectAdminForm
    inlines=[ManagedObjectAttributeInline]
    fieldsets=(
        (None,{
            "fields": ("name","is_managed","administrative_domain","activator","profile_name","description")
        }),
        ("Access",{
            "fields": ("scheme","address","port","remote_path")
        }),
        ("Credentials",{
            "fields": ("user","password","super_password")
        }),
        ("SNMP",{
            "fields": ("snmp_ro","snmp_rw","trap_source_ip","trap_community")
        }),
        ("CM",{
            "fields": ("is_configuration_managed","repo_path")
        }),
        ("Rules",{
            "fields": ("config_filter_rule", "config_validation_rule")
        }),
        ("Tags", {
            "fields": ("tags",)
        }),
    )
    list_display=["name", object_status, "profile_name", "address",
                domain_activator,
                "description", "repo_path", action_links]
    list_filter=["is_managed","is_configuration_managed","activator","administrative_domain","profile_name"]
    search_fields=["name","address","repo_path","description"]
    object_class=ManagedObject
    actions=["test_access"]
    ##
    ## Dirty hack to display PasswordInput in admin form
    ##
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ["password","super_password"]:
            kwargs["widget"]=forms.widgets.PasswordInput
            if "request" in kwargs: # For Django 1.1 compatibility
                kwargs.pop("request",None)
            return db_field.formfield(**kwargs)
        return super(ManagedObjectAdmin,self).formfield_for_dbfield(db_field,**kwargs)
    ##
    ## Row-level access control
    ##
    def has_change_permission(self,request,obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_change_permission(self,request)
            
    def has_delete_permission(self,request,obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_delete_permission(self,request)
        
    def queryset(self,request):
        return ManagedObject.queryset(request.user)
        
    def save_model(self, request, obj, form, change):
        # Save before checking
        admin.ModelAdmin.save_model(self,request,obj,form,change)
        # Then check
        if not obj.has_access(request.user):
            raise PermissionDenied()
    ##
    ## Test object access
    ##
    def test_access(self,request,queryset):
        return self.app.response_redirect("test/%s/"%",".join([str(p.id) for p in queryset]))
    test_access.short_description="Test selected object access"
##
## ManagedObject application
##
class ManagedObjectApplication(ModelApplication):
    model=ManagedObject
    model_admin=ManagedObjectAdmin
    menu="Managed Objects"
    ##
    ## Script index
    ##
    def view_scripts(self,request,object_id):
        o=get_object_or_404(ManagedObject,id=int(object_id))
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        p=o.profile_name
        scripts=sorted([(p+"."+x,x) for x in profile_registry[p].scripts.keys()])
        return self.render(request,"scripts.html",{"object":o,"scripts":scripts})
    view_scripts.url=r"^(?P<object_id>\d+)/scripts/$"
    view_scripts.url_name="scripts"
    view_scripts.access=HasPerm("change")
    ##
    ## Execute script
    ##
    def view_script(self,request,object_id,script):
        # Run map/reduce task
        def run_task(**kwargs):
            task=ReduceTask.create_task([o],script_reduce,{},script,kwargs,None)
            return self.response_redirect("sa:managedobject:scriptresult",object_id,script,task.id)
        #
        o=get_object_or_404(ManagedObject,id=int(object_id))
        # Check user has access to object
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        # Check script exists
        try:
            scr=script_registry[script]
        except:
            return self.response_not_found("No script found")
        form=None
        result=None
        if scr.implements and scr.implements[0].requires_input():
            # Script requires additional parameters
            if request.POST:
                form=scr.implements[0].get_form(request.POST) #<<<?>>> need to combine interfaces
                if form.is_valid():
                    return run_task(**form.cleaned_data)
            else:
                form=scr.implements[0].get_form()
        else:
            # Run scripts without parameters
            return run_task()
        return self.render(request,"script_form.html",{"object":o,"script":script,"form":form})
    view_script.url=r"^(?P<object_id>\d+)/scripts/(?P<script>[^/]+)/$"
    view_script.url_name="script"
    view_script.access=HasPerm("change")
    ##
    ## Wait for script completion and show results
    ##
    def view_scriptresult(self,request,object_id,script,task_id):
        object=get_object_or_404(ManagedObject,id=int(object_id))
        task=get_object_or_404(ReduceTask,id=int(task_id))
        # Check script exists
        try:
            scr=script_registry[script]
        except:
            return self.response_not_found("No script found")
        # Wait for task completion
        try:
            result=task.get_result(block=False)
        except ReduceTask.NotReady:
            return self.render_wait(request,subject="Script %s"%script,text="Processing script. Please wait ...")
        # Format result
        if isinstance(result,basestring):
            pass # Do not convert strings
        else:
            result=pprint.pformat(result)
        return self.render(request,"script_result.html",{"object":object,"script":script,"result":result})
    view_scriptresult.url=r"^(?P<object_id>\d+)/scripts/(?P<script>[^/]+)/(?P<task_id>\d+)/$"
    view_scriptresult.url_name="scriptresult"
    view_scriptresult.access=HasPerm("change")
    ##
    ## AJAX lookup
    ##
    def view_lookup(self,request):
        def lookup_function(q):
            for m in ManagedObject.objects.filter(name__istartswith=q):
                yield m.name
        return self.lookup(request,lookup_function)
    view_lookup.url=r"^lookup/$"
    view_lookup.url_name="lookup"
    view_lookup.access=Permit()
    ##
    ## Test managed objects access
    ##
    def view_test(self,request,objects):
        r=[]
        for mo in [ManagedObject.objects.get(id=int(x)) for x in objects.split(",")]:
            r+=[{
                "object" : mo,
                "users"  : sorted([u.username for u in mo.granted_users]),
                "groups" : sorted([g.name for g in mo.granted_groups]),
                }]
        return self.render(request,"test.html",{"data":r})
    view_test.url=r"^test/(?P<objects>\d+(?:,\d+)*)/$"
    view_test.access=HasPerm("change")
    ##
    ## Display all managed object's addresses
    ##
    def view_addresses(self,request,object_id):
        o=get_object_or_404(ManagedObject,id=int(object_id))
        return self.render(request,"addresses.html",{"addresses":o.address_set.order_by("address"),"object":o})
    view_addresses.url=r"(?P<object_id>\d+)/addresses/"
    view_addresses.url_name="addresses"
    view_addresses.access=HasPerm("change")
    
    ##
    ## Display all attributes
    ##
    @view(  url=r"(?P<object_id>\d+)/attributes/",
            url_name="attributes",
            access=HasPerm("change"))
    def view_attributes(self,request,object_id):
        o=get_object_or_404(ManagedObject,id=int(object_id))
        return self.render(request,"attributes.html",{"attributes":o.managedobjectattribute_set.order_by("key"),"object":o})
    
    ##
    def user_access_list(self,user):
        return [s.selector.name for s in UserAccess.objects.filter(user=user)]
    ##
    def user_access_change_url(self,user):
        return self.site.reverse("sa:useraccess:changelist",QUERY={"user__id__exact":user.id})
    ##
    def group_access_list(self,group):
        return [s.selector.name for s in GroupAccess.objects.filter(group=group)]
    ##
    def group_access_change_url(self,group):
        return self.site.reverse("sa:groupaccess:changelist",QUERY={"group__id__exact":group.id})

