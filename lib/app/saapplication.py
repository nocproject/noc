# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activation Application class
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from application import Application,HasPerm
from django import forms
from django.shortcuts import get_object_or_404
from noc.sa.models import *
from simplereport import *
import types
##
##
##
class SAApplication(Application):
    menu=None        # Menu title
    map_task=None    # Map task name
    reduce_task=None # Reduce task pyRule
    form=None        # Map task parameters
    timeout=60       # Reduce task timeout
    objects=None     # Pre-selected objects
    ##
    def get_menu(self):
        return self.menu
    ##
    ## Return reduce script parameters
    ## from cleaned form data.
    ## By default - all parameters starting with reduce_ 
    ##
    def clean_reduce(self,data):
        return dict([(k[7:],v) for k,v in data.items() if k.startswith("reduce_")])
    ##
    ## Return map scrip t parameters from cleaned form data.
    ## By default - all parameters starting with map_
    ##
    def clean_map(self,data):
        return dict([(k[4:],v) for k,v in data.items() if k.startswith("map_")])
    ##
    ## Display a list of selectors
    ##
    def view_index(self,request):
        if self.objects and self.form is None:
            # Start task immediately
            task=ReduceTask.create_task(
                object_selector=self.objects,
                reduce_script=self.reduce_task,
                reduce_script_params=self.clean_reduce({}),
                map_script=self.map_task,
                map_script_params=self.clean_map({}),
                timeout=self.timeout
            )
            return self.response_redirect("task/%d/"%task.id)
        # Display selectors and form
        selectors=ManagedObjectSelector.objects.filter(is_enabled=True).order_by("name")
        return self.render(request,"sa_app_index.html",{"selectors":selectors})
    view_index.url=r"^$"
    view_index.url_name="index"
    view_index.menu=get_menu
    view_index.access=HasPerm("run")
    ##
    ## Display Form
    ##
    def view_form(self,request,selector_id):
        selector=get_object_or_404(ManagedObjectSelector,id=int(selector_id))
        form=None
        if request.POST:
            # Check form if applicable
            if self.form:
                form=self.form(request.POST)
            if not form or form.is_valid():
                # Prepare parameters
                if form:
                    reduce_script_params=self.clean_reduce(form.cleaned_data)
                    map_script_params=self.clean_map(form.cleaned_data)
                else:
                    reduce_script_params={}
                    map_script_params={}
                # Fetch selected objects
                objects=ManagedObject.objects.filter(id__in=[int(n[4:]) for n in request.POST.keys() if n.startswith("OBJ:")])
                task=ReduceTask.create_task(
                    object_selector=objects,
                    reduce_script=self.reduce_task,
                    reduce_script_params=reduce_script_params,
                    map_script=self.map_task,
                    map_script_params=map_script_params,
                    timeout=self.timeout
                )
                return self.response_redirect("../../task/%d/"%task.id)
        else:
            if self.form:
                # Display empty form if applicable
                form=self.form()
        if type(self.map_task) in [types.ListType,types.TupleType]:
            objects=selector.objects_with_scripts(self.map_task)
        else:
            objects=selector.objects_with_scripts([self.map_task])
        return self.render(request,"sa_app_form.html",{"objects": sorted(objects,lambda x,y: cmp(x.name,y.name)),"form":form})
    view_form.url=r"^selector/(?P<selector_id>\d+)/$"
    view_form.url_name="form"
    view_form.access=HasPerm("run")
    ##
    ## Wait for task completion and display results
    ##
    def view_task(self,request,task_id):
        task=get_object_or_404(ReduceTask,id=int(task_id))
        try:
            result=task.get_result(block=False)
        except ReduceTask.NotReady:
            # Task not ready, refresh
            total_tasks=task.maptask_set.count()
            complete_task=task.maptask_set.filter(status="C").count()
            progress=float(complete_task)*100.0/float(total_tasks)
            return self.render_wait(request,subject="Task",text="Processing task. Please wait ...",progress=progress)
        if isinstance(result,Report):
            # Convert report instance to HTML
            result=result.to_html()
        return self.render(request,"sa_app_result.html",{"result":result})
    view_task.url=r"^task/(?P<task_id>\d+)/$"
    view_task.url_name="task"
    view_task.access=HasPerm("run")
