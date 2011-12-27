# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.mrt application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.models import MRTConfig, ManagedObjectSelector, ManagedObject,\
                          ReduceTask
from noc.lib.serialize import json_decode


class MRTAppplication(ExtApplication):
    """
    sa.mrt application
    """
    def extra_permissions(self):
        """
        Get list of additional permissions
        :return:
        """
        x = set([p.permission_name for p in
                 MRTConfig.objects.filter(is_active=True)])
        return list(x)

    @view(url="^(?P<task>[0-9a-zA-Z_\-]+)/$", method=["POST"],
          access="launch", api=True)
    def api_run(self, request, task):
        """
        Run new MRT
        :param request:
        :param task:
        :return:
        """
        # Get task
        config = MRTConfig.objects.filter(name=task, is_active=True).first()
        if not config:
            return self.response_not_found("Task not found")
        # Check permissions
        if not request.user.has_perm("sa:mrt:%s" % config.permission_name):
            return self.response_forbidden("Permission denied")
        # Parse request
        try:
            r = json_decode(request.raw_post_data)
        except Exception, why:
            return self.response_bad_request(str(why))
        if type(r) != dict:
            return self.response_bad_request("dict required")
        if "selector" not in r:
            return self.response_bad_request("'selector' is missed")
        # Resolve objects from selector
        try:
            objects = ManagedObjectSelector.resolve_expression(r["selector"])
        except ManagedObjectSelector.DoesNotExist, why:
            return self.response_not_found(str(why))
        except ManagedObject.DoesNotExist, why:
            return self.response_not_found(str(why))
        # Check all objects fall within MRTConfig selector
        unauthorized = set(objects).difference(set(
            config.selector.managed_objects))
        if unauthorized:
            return self.response_forbidden("Unauthorized objects: %s" % (
                ", ".join([o.name for o in unauthorized])
            ))
        # Run MRT
        timeout = r.get("timeout", None) or config.timeout
        t = ReduceTask.create_task(objects,
                                   "pyrule:%s" % config.reduce_pyrule.name, {},
                                   config.map_script, r.get("map_args", {}),
                                   timeout)
        return self.response_accepted(location="/sa/mrt/%s/%d/" % (task, t.id))

    @view(url="^(?P<task>[0-9a-zA-Z_\-]+)/(?P<task_id>\d+)/$", method=["GET"],
          access="launch", api=True)
    def api_result(self, request, task, task_id):
        # Get task
        config = MRTConfig.objects.filter(name=task, is_active=True).first()
        if not config:
            return self.response_not_found("Task not found")
        # Check permissions
        if not request.user.has_perm("sa:mrt:%s" % config.permission_name):
            return self.response_forbidden("Permission denied")
        #
        t = self.get_object_or_404(ReduceTask, id=int(task_id))
        try:
            r = t.get_result(block=False)
        except ReduceTask.NotReady:
            # Not ready
            completed = t.maptask_set.filter(status__in=("C", "F")).count()
            total = t.maptask_set.count()
            return {
                "ready": False,
                "progress": int(completed * 100 / total),
                "max_timeout": (t.stop_time - datetime.datetime.now()).seconds,
                "result": None
            }
        # Return result
        return {
            "ready": True,
            "progress": 100,
            "max_timeout": 0,
            "result": r
        }
