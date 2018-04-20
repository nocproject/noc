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
        def oq(s):
            return str(s.id) if s else None

        wf = self.get_object_or_404(Workflow, id=wf_id)
        r = []
        x = 70
        sn = wf.start_node
        for n in Node.objects.filter(workflow=wf.id):
            r += [{
                "type": "node",
                "id": str(n.id),
                "name": n.name,
                "label": n.label or n.name,
                "description": n.description,
                "handler": n.handler,
                "conditional": n.handler_class.conditional,
                "params": n.params,
                "next_node": oq(n.next_node),
                "next_true_node": oq(n.next_true_node),
                "next_false_node": oq(n.next_false_node),
                "x": n.x or x,
                "y": n.y or 50,
                "start": str(n.id) == sn
            }]
            x += 110
        return r

    @view(url=r"^handlers/$", method=["GET"], access="view", api=True)
    def api_handlers(self, request):
        def f(h):
            return {
                "conditional": h.conditional,
                "params": list(h.params)
            }
        return dict((n, f(handlers[n])) for n in handlers)

    @view(url=r"^(?P<wf_id>[0-9a-f]{24})/nodes/$", method=["POST"],
          access="view", api=True, validate=DictListParameter)
    def api_save_nodes(self, request, wf_id):
        def get_by_id(nid):
            if not nid:
                return None
            return Node.objects.filter(id=id_map.get(nid, nid)).first()

        wf = self.get_object_or_404(Workflow, id=wf_id)
        data = json_decode(request.raw_post_data)
        id_map = {}  # JSON -> DB id
        # Process changed nodes
        for r in data:
            if r["type"] == "node":
                if r["id"] and r.get("deleted"):
                    # Delete node
                    n = self.get_object_or_404(Node, id=r["id"])
                    n.delete()
                    continue
                if not r.get("handler"):
                    continue
                # Create/change node
                if r["id"] and not r["id"].startswith("id:"):
                    n = self.get_object_or_404(Node, id=r["id"])
                else:
                    n = Node(workflow=wf)
                n.name = r["name"]
                n.label = r.get("label")
                n.description = r["description"]
                n.handler = r["handler"]
                n.params = r["params"]
                n.x = r["x"]
                n.y = r["y"]
                if not r.get("next_node"):
                    n.next_node = None
                if not r.get("next_true_node"):
                    n.next_true_node = None
                if not r.get("next_false_node"):
                    n.next_false_node = None
                n.save()
                id_map[r["id"]] = n.id
                if r.get("start"):
                    # Move start node
                    wf.start_node = str(n.id)
                    wf.save()
        # Process changed edges
        for r in data:
            if r["type"] == "node":
                if r["id"] and r.get("deleted"):
                    continue
                n = get_by_id(r["id"])
                n.next_node = get_by_id(r.get("next_node"))
                n.next_true_node = get_by_id(r.get("next_true_node"))
                n.next_false_node = get_by_id(r.get("next_false_node"))
                n.save()  # @todo: Eliminate redundant save
        return True
