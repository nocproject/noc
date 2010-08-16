# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map/Reduce tasks
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import Application,HasPerm
from noc.sa.models import ReduceTask,ManagedObjectSelector,script_registry
from noc.main.models import PyRule
##
map_scripts=[(x,x) for x in sorted(set([x.split(".")[2] for x in script_registry.classes.keys() if not x.startswith("Generic.")]))]
##
## Map/Reduce tasks
##
class MRTaskAppplication(Application):
    title="Run Map/Reduce Task"
    ##
    ## Map/Reduce Task Form
    ##
    class MRTaskForm(forms.Form):
        selector=forms.ModelChoiceField(queryset=ManagedObjectSelector.objects)
        reduce_script=forms.ModelChoiceField(queryset=PyRule.objects.filter(interface="IReduceTask").order_by("name"))
        reduce_script_params=forms.CharField(required=False,help_text="Python expression to be passed as reduce script arguments")
        map_script=forms.ChoiceField(choices=map_scripts)
        map_script_params=forms.CharField(required=False,help_text="Python expression to be passed as map script arguments")
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
    ##
    ## Run new task
    ##
    def view_run(self,request):
        if request.POST:
            form=self.MRTaskForm(request.POST)
            if form.is_valid():
                t=ReduceTask.create_task(
                    object_selector=form.cleaned_data["selector"],
                    reduce_script="pyrule:"+form.cleaned_data["reduce_script"].name,
                    reduce_script_params=form.cleaned_data["reduce_script_params"],
                    map_script=form.cleaned_data["map_script"],
                    map_script_params=form.cleaned_data["map_script_params"],
                    timeout=form.cleaned_data["timeout"]
                )
                return self.response_redirect_to_object(t)
        else:
            form=self.MRTaskForm(initial={"timeout":180})
        return self.render(request,"mr_task.html",{"form":form})
    view_run.url=r"^$"
    view_run.menu="Tasks | Run Task"
    view_run.access=HasPerm("run")
    ##
    ## Show task result
    ##
    def view_result(self,request,task_id):
        task=get_object_or_404(ReduceTask,id=int(task_id))
        try:
            result=task.get_result(block=False)
        except ReduceTask.NotReady:
            return self.render_wait(request,subject="Running task",text="Processing task. Please wait...")
        return self.render(request,"mr_task_result.html",{"result":result})
    view_result.url=r"^(?P<task_id>\d+)/$"
    view_result.url_name="task"
    view_result.access=HasPerm("run")
