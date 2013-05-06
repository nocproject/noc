# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## wf.workflow application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.wf.models.workflow import Workflow
from noc.wf.models.variable import Variable
from noc.wf.models.lane import Lane
from noc.wf.models.node import Node
from noc.lib.app.docinline import DocInline
from noc.wf.handlers import handlers
from noc.sa.interfaces.base import DictListParameter
from noc.lib.serialize import json_decode


class WorkflowApplication(ExtDocApplication):
    """
    Workflow application
    """
    title = "Workflow"
    menu = "Setup | Workflows"
    model = Workflow

    lanes = DocInline(Lane)
    variables = DocInline(Variable)

    @view(url=r"^(?P<wf_id>[0-9a-f]{24})/nodes/$", method=["GET"],
          access="view", api=True)
    def api_nodes(self, request, wf_id):
        wf = self.get_object_or_404(Workflow, id=wf_id)
        r = []
        x = 70
        sn = wf.start_node
        for n in Node.objects.filter(workflow=wf.id):
            r += [{
                "type": "node",
                "id": str(n.id),
                "name": n.name,
                "description": n.description,
                "handler": n.handler,
                "conditional": n.handler_class.conditional,
                "params": n.params,
                "next_node": n.next_node,
                "next_true_node": n.next_true_node,
                "next_false_node": n.next_false_node,
                "x": n.x or x,
                "y": n.y or 50,
                "start": n.name == sn
            }]
            x += 110
        return r

    @view(url=r"^handlers/$", method=["GET"], access="view", api=True)
    def api_handlers(self, request):
        return dict((n, None) for n in handlers)

    @view(url=r"^(?P<wf_id>[0-9a-f]{24})/nodes/$", method=["POST"],
          access="view", api=True, validate=DictListParameter)
    def api_node(self, request, wf_id):
        wf = self.get_object_or_404(Workflow, id=wf_id)
        data = json_decode(request.raw_post_data)
        for r in data:
            if r["type"] == "node":
                if r["id"]:
                    n = self.get_object_or_404(Node, id=r["id"])
                else:
                    n = Node()
                n.name = r["name"]
                n.x = r["x"]
                n.y = r["y"]
                n.save()
        return True
