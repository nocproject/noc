# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map/Reduce tasks
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import Application
from noc.sa.models import script_registry,ReduceTask,ManagedObjectSelector,reduce_script_registry
##
## Available scripts
##
map_script_choices=[(x,x) for x in sorted(set([x.split(".")[2] for x in script_registry.classes.keys() if not x.startswith("Generic.")]))]
##
## Map/Reduce Task Form
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
##
## Map/Reduce tasks
##
class MRTaskAppplication(Application):
    title="Run Map/Reduce Task"
    ##
    ## Run new task
    ##
    def view_run(self,request):
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
                return self.response_redirect(self.base_url+"%d/"%t.id)
        else:
            form=MRTaskForm(initial={"timeout":180})
        return self.render(request,"mr_task.html",{"form":form})
    view_run.url=r"^$"
    view_run.menu="Map/Reduce Tasks"
    view_run.access=Application.has_perm("sa.add_reducetask")
    ##
    ## Show task result
    ##
    def view_result(self,request,task_id):
        task=get_object_or_404(ReduceTask,id=int(task_id))
        if not task.complete: # Render wait page
            return self.render_wait(request,subject="map/reduce task") 
        result=task.get_result()
        task.delete()
        return self.render(request,"mr_task_result.html",{"result":result})
    view_result.url=r"^(?P<task_id>\d+)/$"
    view_result.access=Application.has_perm("sa.add_reducetask")
