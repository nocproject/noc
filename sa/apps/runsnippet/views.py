# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parallel command execution
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import new
## Django modules
from django import forms
from django.utils.datastructures import SortedDict
## NOC modules
from noc.lib.app import Application, view, NOCForm
from noc.sa.models.commandsnippet import CommandSnippet
from noc.sa.models.reducetask import ReduceTask
from noc.sa.models.managedobject import ManagedObject
from noc.main.models import Permission
from noc.lib.mac import MAC


## Form clean for mac address
def clean_mac(self, v):
    # Call basic clean
    v = forms.CharField.clean(self, v)
    # Normalize and clean MAC
    try:
        return MAC(v.strip())
    except ValueError:
        raise forms.ValidationError("Invalid MAC")

CLEAN = {
    "mac": clean_mac
}


def reduce_task(task, snippet):
    r = ["<style>.cmd {border-bottom: 1px solid black;font-weight: bold;}</style>"]
    r += ["<table border='1'>", "<tr><th>Object</th><th>Result</th></tr>"]
    for mt in task.maptask_set.all():
        if mt.status == "C":
            result = "<pre>" + "<br/>".join(mt.script_result) + "</pre>"
            icon = "yes"
        else:
            result = "<pre>%s</pre>" % str(mt.script_result)
            icon = "no"
        r += ["<tr>", "<td>",
              "<img src='/media/admin/img/icon-%s.gif' />" % icon,
              "&nbsp;",
              mt.managed_object.name, "</td>",
              "<td>", result, "</td>", "</tr>"]
    r += ["</table>"]
    return "".join(r)


class RunSnippetApplication(Application):
    title = "Run Snippet"

    def extra_permissions(self):
        x = set([s.permission_name
                 for s in
                 CommandSnippet.objects.filter(permission_name__isnull=False)])
        return list(x)
    
    def get_map_script(self, snippet):
        if snippet.change_configuration:
            return "configure"
        else:
            return "commands"
    
    def get_form(self, vars, data=None):
        """
        Create form
        :param vars: CommandSnippet.vars
        :param data:
        :return:
        """
        fields = []
        for v in vars:
            type = vars[v]["type"]
            if type in ("internal", "hidden"):
                continue
            required = vars[v].get("required", False)
            label = vars[v].get("label", v)
            if type == "bool":
                ff = forms.BooleanField(label=label, required=required)
            elif type == "int":
                ff = forms.IntegerField(label=label, required=required)
            else:
                ff = forms.CharField(label=label, required=required)
                c = CLEAN.get(type)
                if c:
                    ff.clean = new.instancemethod(c, ff, ff.__class__)
            fields += [(v, ff)]
        # Apply data
        class fc(NOCForm):
            pass
        fc.base_fields.update(SortedDict(fields))
        return fc(data)

    def run_task(self, snippet, objects, params):
        def get_map_script_params(snippet, data):
            def inner(obj):
                v = data.copy()
                v["object"] = obj
                return {
                    "commands": snippet.expand(v).splitlines(),
                    "ignore_cli_errors": snippet.ignore_cli_errors
                }
            return inner
        
        map_task = self.get_map_script(snippet)
        task = ReduceTask.create_task(
            object_selector=objects,
            reduce_script=reduce_task,
            reduce_script_params={"snippet": snippet},
            map_script=map_task,
            map_script_params=get_map_script_params(snippet, params),
            timeout=snippet.timeout
        )
        return task.id
    
    @view(url=r"^$", url_name="index", menu="Tasks | Run Snippet",
          access="launch")
    def view_index(self, request):
        """ Display all available snippets"""
        user = request.user
        snippets = [s for s in
                    CommandSnippet.objects.filter(is_enabled=True).order_by("name")
                    if (s.permission_name is None or
                        Permission.has_perm(user, s.effective_permission_name))]
        return self.render(request, "snippets.html", snippets=snippets)
    
    @view(url=r"^(?P<snippet_id>\d+)/$", url_name="snippet",
        access="launch")
    def view_snippet(self, request, snippet_id):
        """
        Snippet parameters and object selection form
        """
        snippet = self.get_object_or_404(CommandSnippet, id=int(snippet_id))
        if (snippet.permission_name and
            not Permission.has_perm(request.user,
                                    snippet.effective_permission_name)):
            return self.response_forbidden("Forbidden")
        vars = snippet.vars
        has_vars = any([v for v in vars if vars[v]["type"] not in (
            "internal", "hidden")])
        map_task = self.get_map_script(snippet)
        objects = list(snippet.selector.objects_for_user(request.user,
                                                         [map_task]))
        form = None
        if request.POST:
            objects = ManagedObject.objects.filter(id__in=[
                int(n[4:]) for n in request.POST.keys()
                if n.startswith("OBJ:") or n.startswith("CFM:")])
            data = None
            if has_vars:
                form = self.get_form(vars, request.POST)
                if form.is_valid():
                    data = form.cleaned_data
            else:
                data = {}
            if data is not None:
                if (not snippet.require_confirmation or
                    "__confirmed" in request.POST):
                    task = self.run_task(snippet, objects, data)
                    return self.response_redirect("sa:runsnippet:task",
                                                  snippet.id, task)
                elif snippet.require_confirmation:
                    cd = []
                    for o in objects:
                        d = data.copy()
                        d.update({"object": o})
                        cd += [(o, snippet.expand(d))]
                    return self.render(request, "confirm.html",
                        data=cd, snippet=snippet, vars = data.items())
        else:
            if (not has_vars and len(objects) == 1 and
                    not snippet.require_confirmation):
                # Run immediately
                task = self.run_task(snippet, objects, {})
                return self.response_redirect("sa:runsnippet:task",
                                              snippet.id, task)
            elif vars:
                form = self.get_form(vars)
        # Display form
        return self.render(request, "form.html", snippet=snippet,
                objects=objects, form=form)
    
    @view(url=r"^(?P<snippet_id>\d+)/task/(?P<task_id>\d+)/$",
        url_name="task", access="launch")
    def view_task(self, request, snippet_id, task_id):
        """
        Wait for task completion and render result
        """
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
    
