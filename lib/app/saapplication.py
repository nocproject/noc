# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activation Application class
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from application import Application, view
from noc.sa.models import *
from simplereport import *


class SAApplication(Application):
    menu = None         # Menu title
    map_task = None     # Map task name
    reduce_task = None  # Reduce task pyRule
    form = None         # Map task parameters
    timeout = 60        # Reduce task timeout. None - for adaptive timeouts
    objects = None      # Pre-selected objects

    def get_menu(self):
        return self.menu

    def clean_reduce(self, data):
        """
        Prepare reduce script parameters from cleaned form data.
        By default, all parameters starting with reduce_ will be included
        :param data:
        :return: dict of reduce parameters
        """
        return dict(
            [(k[7:], v) for k, v in data.items() if k.startswith("reduce_")])

    def clean_map(self, data):
        """
        Prepare map script parameters from cleaned form data.
        Dy default, all parameters starting with map_ will be included
        :param data:
        :return: dict of map script parameters
        """
        return dict(
            [(k[4:], v) for k, v in data.items() if k.startswith("map_")])

    def render_result(self, request, result):
        return self.render(request, "sa_app_result.html", {"result": result})

    @view(url=r"^$", url_name="index", menu=get_menu, access="run")
    def view_index(self, request):
        """
        Display a list of selectors
        :param request:
        :return:
        """
        if self.objects and self.form is None:
            # Start task immediately
            task = ReduceTask.create_task(
                object_selector=self.objects,
                reduce_script=self.reduce_task,
                reduce_script_params=self.clean_reduce({}),
                map_script=self.map_task,
                map_script_params=self.clean_map({}),
                timeout=self.timeout
            )
            return self.response_redirect("task/%d/" % task.id)
        # Display selectors and form
        selectors = ManagedObjectSelector.objects.filter(
            is_enabled=True).order_by("name")
        return self.render(request, "sa_app_index.html",
                {"selectors": selectors})

    @view(url=r"^selector/(?P<selector_id>\d+)/$", url_name="form",
          access="run")
    def view_form(self, request, selector_id):
        """
        Display form
        :param request:
        :param selector_id:
        :return:
        """
        selector = get_object_or_404(ManagedObjectSelector,
                                     id=int(selector_id))
        form = None
        if request.POST:
            # Check form if applicable
            if self.form:
                form = self.form(request.POST)
            if not form or form.is_valid():
                # Prepare parameters
                if form:
                    reduce_script_params = self.clean_reduce(form.cleaned_data)
                    map_script_params = self.clean_map(form.cleaned_data)
                else:
                    reduce_script_params = {}
                    map_script_params = {}
                # Fetch selected objects
                objects = ManagedObject.objects.filter(
                    id__in=[int(n[4:]) for n in request.POST.keys() if
                            n.startswith("OBJ:")])
                task = ReduceTask.create_task(
                    object_selector=objects,
                    reduce_script=self.reduce_task,
                    reduce_script_params=reduce_script_params,
                    map_script=self.map_task,
                    map_script_params=map_script_params,
                    timeout=self.timeout
                )
                return self.response_redirect("../../task/%d/" % task.id)
        else:
            if self.form:
                # Display empty form if applicable
                form = self.form()
        if type(self.map_task) in [types.ListType, types.TupleType]:
            objects = selector.objects_with_scripts(self.map_task)
        else:
            objects = selector.objects_with_scripts([self.map_task])
        return self.render(request, "sa_app_form.html",
                {"objects": sorted(objects, lambda x, y: cmp(x.name, y.name)),
                 "form": form})

    @view(url=r"^task/(?P<task_id>\d+)/$", url_name="task", access="run")
    def view_task(self, request, task_id):
        """
        Wait for task completion and display results
        :param request:
        :param task_id:
        :return:
        """
        task = get_object_or_404(ReduceTask, id=int(task_id))
        try:
            result = task.get_result(block=False)
        except ReduceTask.NotReady:
            # Task not ready, refresh
            total_tasks = task.maptask_set.count()
            complete_task = task.maptask_set.filter(status="C").count()
            progress = float(complete_task) * 100.0 / float(total_tasks)
            return self.render_wait(request, subject="Task",
                                    text="Processing task. Please wait ...",
                                    progress=progress)
        if isinstance(result, Report):
            # Convert report instance to HTML
            result = result.to_html()
        return self.render_result(request, result)
