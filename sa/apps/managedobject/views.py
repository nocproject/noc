# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User,Group
from noc.lib.app import ModelApplication,site,Permit,PermitSuperuser,HasPerm,PermissionDenied
from noc.sa.models import *
from noc.settings import config
from noc.lib.fileutils import in_dir
import pprint,types,socket,csv,os
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
        r+=[("Config","cm:config:view",[obj.config.id])]
    except:
        pass
    try:
        obj.profile
        r+=[("Scripts","sa:managedobject:scripts",[obj.id])]
    except:
        pass
    return "<br/>".join(["<a href='%s'>%s</a>"%(site.reverse(view,*params),title) for title,view,params in r])
action_links.short_description="Actions"
action_links.allow_tags=True
##
## Display object status
##
def object_status(o):
    s=[]
    if o.is_managed:
        s+=["Managed"]
    if o.is_configuration_managed:
        s+=["Configuration"]
    return "<br/>".join(s)
object_status.short_description="Status"
object_status.allow_tags=True
##
## Reduce task for script results
##
def script_reduce(task):
    mt=task.maptask_set.all()[0]
    if mt.status!="C":
        return "Task failed: "+str(mt.script_result)
    return mt.script_result
##
## ManagedObject admin
##
class ManagedObjectAdmin(admin.ModelAdmin):
    form=ManagedObjectAdminForm
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
        ("Tags", {
            "fields": ("tags",)
        }),
    )
    list_display=["name",object_status,"profile_name","address","administrative_domain","activator","description","repo_path",action_links]
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
    ## Form for uploading managed objects
    ##
    class MOUploadForm(forms.Form):
        administrative_domain=forms.ModelChoiceField(queryset=AdministrativeDomain.objects)
        activator=forms.ModelChoiceField(queryset=Activator.objects)
        file=forms.FileField()
    ##
    ## Managed objects tools
    ##
    def view_tools(self,request):
        return self.render(request,"tools.html",{"upload_mo_form":self.MOUploadForm()})
    view_tools.url=r"^tools/$"
    view_tools.url_name="tools"
    view_tools.access=PermitSuperuser()
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
            task=ReduceTask.create_task([o],script_reduce,{},script,kwargs,60)
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
            return self.render_wait(request,subject="Script %s"%script,text="Processing scirpt. Please wait ...")
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
    ## Upload managed objects
    ##
    def view_upload(self,request):
        def upload_csv(file):
            count=0
            reader=csv.reader(file)
            rows=list(reader)
            if len(rows)<=1:
                return 0
            # First row is a field names
            header=rows.pop(0)
            # Check field names
            for c in header:
                if c not in MO_IMPORT_CSV_FIELDS:
                    return 0,"Invalid field '%s'"%c
            # Check all required fields present
            for c in MO_IMPORT_REQUIRED_CSV_FIELDS:
                if c not in header:
                    return 0,"Required fields '%s' is missed"%c
            # Check rows
            for row in rows:
                vars=dict(zip(header,row)) # Convert row to hash: field->value
                if not vars: # Skip empty lines
                    continue 
                try:
                    o=ManagedObject.objects.get(name=vars["name"]) # Find existing object
                except ManagedObject.DoesNotExist:
                    o=ManagedObject(name=vars["name"])# Or create new
                for k,v in vars.items():
                    if k=="name": # "name" is already processed
                        continue
                    if k=="profile_name" and v not in profile_registry.classes:
                        return 0,"Invalid profile '%s' at line %d"%(v,count+1)
                    if not v: # Skip empty fields
                        continue
                    if k=="port": # Convert port to integer
                        try:
                            v=int(v)
                        except:
                            return 0,"Invalid port: %s at line %d"%(v,count+1)
                    if k=="scheme":
                        try:
                            v=SCHEME[v]
                        except KeyError:
                            return 0,"Invalid access scheme %s at line %d"%(v,count+1)
                    if k=="repo_path": # Set is_configuration_managed if repo_path given
                        o.is_configuration_managed=True
                    setattr(o,k,v) # Finally set attribute
                o.administrative_domain=administrative_domain
                o.activator=activator
                o.save() # Perform SQL statement
                count+=1
            return count,None
        MO_IMPORT_CSV_FIELDS=["name","profile_name","description","scheme","address","port","user","password",
            "super_password","remote_path","trap_source_ip","trap_community","snmp_ro","snmp_rw","repo_path"]
        MO_IMPORT_REQUIRED_CSV_FIELDS=["name","profile_name","scheme","address","repo_path"]
        SCHEME=dict([(x[1],x[0]) for x in scheme_choices])
        # Process request
        if not request.user.is_superuser:
            return self.response_forbidden("Access Denied")
        if request.method=="POST":
            form = self.MOUploadForm(request.POST, request.FILES)
            if form.is_valid():
                administrative_domain=form.cleaned_data["administrative_domain"]
                activator=form.cleaned_data["activator"]
                count,error=upload_csv(request.FILES['file'])
                if error:
                    return self.render_failure(request,"Managed Object Upload Failure",error)
                else:
                    return self.render_success(request,"Managed Objects are Uploaded","%d managed objects uploaded/updated"%count)
        return self.response_redirect(self.base_url+"tools/")
    view_upload.url=r"^tools/upload/$"
    view_upload.url_name="upload"
    view_upload.access=PermitSuperuser()
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

