# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SA module views.py
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.shortcuts import get_object_or_404
from django import forms
from noc.lib.render import render, render_success, render_failure, render_wait
from noc.sa.models import ManagedObject,script_registry,profile_registry,AdministrativeDomain,Activator,scheme_choices,ManagedObjectSelector,\
    ReduceTask, reduce_script_registry, script_registry, TaskSchedule
from django.http import HttpResponseForbidden,HttpResponseNotFound,HttpResponseRedirect
from django.views.generic import list_detail
from xmlrpclib import ServerProxy, Error
from noc.settings import config
from django.contrib.auth.decorators import permission_required
import pprint,types,socket,csv,datetime

##
## Display a list of object's scripts
##
def object_scripts(request,object_id):
    o=get_object_or_404(ManagedObject,id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    p=o.profile_name
    scripts=sorted([(p+"."+x,x) for x in profile_registry[p].scripts.keys()])
    return render(request,"sa/scripts.html",{"object":o,"scripts":scripts})
##
## Execute object script
##
def object_script(request,object_id,script):
    def get_result(script,object_id,**kwargs):
        server=ServerProxy("http://%s:%d"%(config.get("xmlrpc","server"),config.getint("xmlrpc","port")))
        try:
            result=server.script(script,object_id,kwargs)
        except socket.error,why:
            raise Exception("XML-RPC socket error: "+why[1])
        if type(result) not in [types.StringType,types.UnicodeType]:
            result=pprint.pformat(result)
        return result
        
    o=get_object_or_404(ManagedObject,id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    try:
        scr=script_registry[script]
    except:
        return HttpResponseNotFound("No script found")
    form=None
    result=None
    if scr.implements and scr.implements[0].requires_input():
        if request.POST:
            form=scr.implements[0].get_form(request.POST) #<<<?>>> need to combine interfaces
            if form.is_valid():
                data={}
                for k,v in form.cleaned_data.items():
                    if v:
                        data[k]=v
                try:
                    result=get_result(script,object_id,**data)
                except Exception,why:
                    return render_failure(request,"Script Failed",why)
        else:
            form=scr.implements[0].get_form()
    else:
        try:
            result=get_result(script,object_id)
        except Exception,why:
            return render_failure(request,"Script Failed",why.faultString)
    return render(request,"sa/script.html",{"object":o,"result":result,"script":script,"form":form})
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
def tools(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")
    return render(request,"sa/tools.html",{"upload_mo_form":MOUploadForm()})
##
## List of CSV file fields
##
MO_IMPORT_CSV_FIELDS=["name","profile_name","description","scheme","address","port","user","password","super_password","remote_path",
    "trap_source_ip","trap_community","snmp_ro","snmp_rw","repo_path"]
MO_IMPORT_REQUIRED_CSV_FIELDS=["name","profile_name","scheme","address","repo_path"]
SCHEME=dict([(x[1],x[0]) for x in scheme_choices])
##
## Upload managed objects from a CSV file
##
def upload_managed_objects(request):
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
    # Process request
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")
    if request.method=="POST":
        form = MOUploadForm(request.POST, request.FILES)
        if form.is_valid():
            administrative_domain=form.cleaned_data["administrative_domain"]
            activator=form.cleaned_data["activator"]
            count,error=upload_csv(request.FILES['file'])
            if error:
                return render_failure(request,"Managed Object Upload Failure",error)
            else:
                return render_success(request,"Managed Objects are Uploaded","%d managed objects uploaded/updated"%count)
    return HttpResponseRedirect("/sa/tools/")
## Script choices
map_script_choices=[(x,x) for x in sorted(set([x.split(".")[2] for x in script_registry.classes.keys() if not x.startswith("Generic.")]))]
##
## Run new Map/Reduce task
##
class MRTaskForm(forms.Form):
    selector=forms.ModelChoiceField(queryset=ManagedObjectSelector.objects)
    reduce_script=forms.ChoiceField(choices=reduce_script_registry.choices)
    reduce_script_params=forms.CharField(required=False)
    map_script=forms.ChoiceField(choices=map_script_choices)
    map_script_params=forms.CharField(required=False)
    timeout=forms.IntegerField()
    def clean_reduce_script_params(self):
        if self.cleaned_data["reduce_script_params"]=="":
            return ""
        try:
            return eval(self.cleaned_data["reduce_script_params"],{},{})
        except SyntaxError:
            raise forms.ValidationError("Invalid syntax")
    def clean_map_script_params(self):
        if self.cleaned_data["map_script_params"]=="":
            return ""
        try:
            return eval(self.cleaned_data["map_script_params"],{},{})
        except SyntaxError:
            raise forms.ValidationError("Invalid syntax")

@permission_required("sa.add_reducetask")
def mr_task(request):
    if request.POST:
        form = MRTaskForm(request.POST)
        if form.is_valid():
            t=ReduceTask.create_task(
                object_selector=form.cleaned_data["selector"],
                reduce_script=form.cleaned_data["reduce_script"],
                reduce_script_params=form.cleaned_data["reduce_script_params"],
                map_script=form.cleaned_data["map_script"],
                map_script_params=form.cleaned_data["map_script_params"],
                timeout=form.cleaned_data["timeout"]
            )
            return HttpResponseRedirect("/sa/mr_task/%d/"%t.id)
    else:
        form=MRTaskForm(initial={"timeout":180})
    return render(request,"sa/mr_task.html",{"form":form})
##
## Get task result
##
@permission_required("sa.add_reducetask")
def mr_task_result(request,task_id):
    task=get_object_or_404(ReduceTask,id=int(task_id))
    if not task.complete: # Render wait page
        return render_wait(request,subject="map/reduce task") 
    result=task.get_result()
    task.delete()
    return render(request,"sa/mr_task_result.html",{"result":result})
