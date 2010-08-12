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
##
##
##
class SAApplication(Application):
    menu=None        # Menu title
    map_task=None    # Map task name
    reduce_task=None # Reduce task pyRule
    form=None        # Map task parameters
    timeout=60       # Reduce task timeout
    ##
    def get_menu(self):
        return self.menu
    ##
    ## Display a list of selectors
    ##
    def view_index(self,request):
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
        if request.POST:
            # Fetch selected objects
            objects=ManagedObject.objects.filter(id__in=[int(n[4:]) for n in request.POST.keys() if n.startswith("OBJ:")])
            task=ReduceTask.create_task(
                object_selector=objects,
                reduce_script=self.reduce_task,
                reduce_script_params={},
                map_script=self.map_task,
                map_script_params={},
                timeout=self.timeout
            )
            return self.response_redirect("../../task/%d/"%task.id)
        else:
            pass
        objects=selector.objects_with_scripts([self.map_task])
        return self.render(request,"sa_app_form.html",{"objects":objects})
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
            return self.render_wait(request,subject="Task",text="Processing task. Please wait ...")
        if isinstance(result,Report):
            # Convert report instance to HTML
            result=result.to_html()
        return self.render(request,"sa_app_result.html",{"result":result})
    view_task.url=r"^task/(?P<task_id>\d+)/$"
    view_task.url_name="task"
    view_task.access=HasPerm("run")
