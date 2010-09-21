# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parallel command execution
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.saapplication import SAApplication
from django import forms
import pprint
##
## Reduce task for commands
##
def reduce_commands(task,commands):
    r=["<style>.cmd {border-bottom: 1px solid black;font-weight: bold;}</style>"]
    r+=["<table border='1'>","<tr><th>Object</th><th>Status</th><th>Result</th></tr>"]
    for mt in task.maptask_set.all():
        if mt.status=="C":
            result="\n".join(["<div class='cmd'>%s</div><br/><pre>%s</pre><br/>"%(c,sr) for c,sr in zip(commands,mt.script_result)])
        else:
            result="<pre>%s</pre>"%str(mt.script_result)
        r+=["<tr>","<td>",mt.managed_object.name,"</td>","<td>",mt.status,"</td>","<td>",result,"</td>","</tr>"]
    r+=["</table>"]
    return "".join(r)
##
##
##
class RunCommandsAppplication(SAApplication):
    title="Run commands"
    menu="Tasks | Run Commands"
    reduce_task=reduce_commands
    map_task="commands"
    
    class CommandsForm(forms.Form):
        commands=forms.CharField(widget=forms.Textarea,
            help_text="Enter a list of commands to execute. One command per a line.")
    form=CommandsForm
    ##
    ## Convert text field to a list of commands
    ##
    def clean_map(self,data):
        return {
            "commands": [c for c in data["commands"].splitlines()]
        }
    ##
    ## Save a list of commands for reduce task
    ##
    def clean_reduce(self,data):
        return {
            "commands": [c for c in data["commands"].splitlines()]
        }