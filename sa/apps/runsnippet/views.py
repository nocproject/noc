# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parallel command execution
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
## NOC modules
from noc.lib.app import Application, HasPerm, view, NOCForm
from noc.sa.models import CommandSnippet, ReduceTask, ManagedObject


def reduce_task(task, snippet):
    r = ["<style>.cmd {border-bottom: 1px solid black;font-weight: bold;}</style>"]
    r += ["<table border='1'>", "<tr><th>Object</th><th>Status</th><th>Result</th></tr>"]
    for mt in task.maptask_set.all():
        if mt.status == "C":
            result = "<pre>" + "<br/>".join(mt.script_result) + "</pre>"
        else:
            result = "<pre>%s</pre>" % str(mt.script_result)
        r += ["<tr>", "<td>", mt.managed_object.name, "</td>",
              "<td>", mt.status, "</td>", "<td>", result, "</td>", "</tr>"]
    r += ["</table>"]
    return "".join(r)


class RunSnippetApplication(Application):
    title = "Run Snippet"
    
    def get_map_script(self, snippet):
        if snippet.change_configuration:
            return "configure"
        else:
            return "commands"
    
    @view(url=r"^$", url_name="index", menu="Tasks | Run Snippet",
        access=HasPerm("run"))
    def view_index(self, request):
        """ Display all available snippets"""
        snippets = CommandSnippet.objects.filter(is_enabled=True).order_by("name")
        return self.render(request, "snippets.html", snippets=snippets)
    
    @view(url=r"^(?P<snippet_id>\d+)/$", url_name="snippet",
        access=HasPerm("run"))
    def view_snippet(self, request, snippet_id):
        def get_form(data=None):
            f = NOCForm(data)
            for v in vars:
                f.fields[v] = forms.CharField(label=v)
            return f
        
        def get_map_script_params(snippet, data):
            def inner(obj):
                v = data.copy()
                v["object"] = obj
                return {"commands": snippet.expand(v).splitlines()}
            return inner
        
        snippet = self.get_object_or_404(CommandSnippet, id=int(snippet_id))
        vars = snippet.vars
        if "object" in vars:
            vars.remove("object")
        map_task = self.get_map_script(snippet)
        objects = list(snippet.selector.objects_with_scripts([map_task]))
        form = None
        if request.POST:
            objects = ManagedObject.objects.filter(id__in=[
                int(n[4:]) for n in request.POST.keys() if n.startswith("OBJ:")])
            data = None
            if vars:
                form = get_form(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
            else:
                data = {}
            if data is not None:
                task = ReduceTask.create_task(
                    object_selector=objects,
                    reduce_script=reduce_task,
                    reduce_script_params={"snippet": snippet},
                    map_script=map_task,
                    map_script_params=get_map_script_params(snippet, data),
                    timeout=snippet.timeout
                )
                return self.response_redirect("sa:runsnippet:task",
                                              snippet.id, task.id)
                
        else:
            if not vars and len(objects) == 1:
                # Run immediately
                task = ReduceTask.create_task(
                    object_selector=objects,
                    reduce_script=reduce_task,
                    reduce_script_params={"snippet": snippet},
                    map_script=map_task,
                    map_script_params=get_map_script_params(snippet, {}),
                    timeout=snippet.timeout
                )
                return self.response_redirect("sa:runsnippet:task",
                                              snippet.id, task.id)
            elif vars:
                form = get_form()
        # Display form
        return self.render(request, "form.html", snippet=snippet,
                objects=objects, form=form)
    
    @view(url=r"^(?P<snippet_id>\d+)/task/(?P<task_id>\d+)/$",
        url_name="task", access=HasPerm("run"))
    def view_task(self, request, snippet_id, task_id):
        snippet = self.get_object_or_404(CommandSnippet, id=int(snippet_id))
        task = self.get_object_or_404(ReduceTask, id=int(task_id))
        try:
            result = task.get_result(block=False)
        except ReduceTask.NotReady:
            # Task not ready, refresh
            total_tasks = task.maptask_set.count()
            complete_task = task.maptask_set.filter(status="C").count()
            progress = float(complete_task) * 100.0 / float(total_tasks)
            return self.render_wait(request, subject="Task",
                text="Processing task. Please wait ...", progress=progress)
        return self.render(request, "result.html", snippet=snippet,
            result=result)
    