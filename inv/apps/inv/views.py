# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.modelinterface import ModelInterface
from noc.lib.validators import is_objectid
from noc.sa.interfaces.base import (StringParameter, ObjectIdParameter,
                                    UnicodeParameter, ListOfParameter)
from noc.lib.utils import deep_copy, deep_merge


class InvApplication(ExtApplication):
    """
    inv.inv application
    """
    title = "Inventory"
    menu = "Inventory"

    def get_root(self):
        """
        Get root container
        """
        if not hasattr(self, "root_container"):
            rm = ObjectModel.objects.get(name="Root")
            rc = list(Object.objects.filter(model=rm))
            if len(rc) == 0:
                raise Exception("No root object")
            elif len(rc) == 1:
                self.root_container = rc[0]
                return self.root_container
            else:
                raise Exception("Multiple root objects")
        else:
            return self.root_container

    @view("^node/$", method=["GET"],
          access="read", api=True)
    def api_node(self, request):
        container = None
        if request.GET and "node" in request.GET:
            container = request.GET["node"]
            if container == "root":
                container = self.get_root().id
            elif not is_objectid(container):
                raise Exception("Invalid node")
        r = []
        if not container:
            container = self.get_root().id
        for o in Object.objects.filter(container=container):
            n = {
                "id": str(o.id),
                "name": o.name
            }
            if o.get_data("container", "container"):
                n["expanded"] = False
            else:
                n["leaf"] = True
            r += [n]
        return r

    @view("^add_group/$", method=["POST"], access="create_group",
          api=True,
          validate={
              "container": ObjectIdParameter(required=False),
              "type": ObjectIdParameter(),
              "name": UnicodeParameter()
          })
    def api_add_group(self, request, type, name, container=None):
        if container is None:
            c = self.get_root()
        else:
            c = self.get_object_or_404(Object, id=container)
        m = self.get_object_or_404(ObjectModel, id=type)
        o = Object(name=name, model=m, container=c.id)
        o.save()
        return str(o.id)

    @view("^insert/$", method=["POST"], access="reorder", api=True,
          validate={
              "container": ObjectIdParameter(required=False),
              "objects": ListOfParameter(element=ObjectIdParameter()),
              "position": StringParameter()
          })
    def api_insert(self, request, container, objects, position):
        c = self.get_object_or_404(Object, id=container)
        o = []
        for r in objects:
            o += [self.get_object_or_404(Object, id=r)]
        if position == "append":
            for x in o:
                x.put_into(c)
        return True

    @view("^(?P<id>[0-9a-f]{24})/data/", method=["GET"],
          access="read", api=True)
    def api_data(self, request, id):
        o = self.get_object_or_404(Object, id=id)
        data = []
        for k, v, d in [
                ("Vendor", o.model.vendor.name, "Hardware vendor"),
                ("Model", o.model.name, "Inventory model"),
                ("Name", o.name, "Inventory name"),
                ("ID", str(o.id), "Internal ID")
            ]:
            data += [{
                "interface": "Common",
                "name": k,
                "value": v,
                "type": "str",
                "description": d,
                "required": True,
                "is_const": True
            }]
        d = deep_merge(o.model.data, o.data)
        for i in d:
            mi = ModelInterface.objects.filter(name=i).first()
            if not mi:
                continue
            for k in d[i]:
                a = mi.get_attr(k)
                if not a:
                    continue
                data += [{
                    "interface": i,
                    "name": k,
                    "value": d[i][k],
                    "type": a.type,
                    "description": a.description,
                    "required": a.required,
                    "is_const": a.is_const
                }]
        return {
            "name": o.name,
            "model": o.model.name,
            "data": data,
            "log": [
                {
                    "ts": x.ts.isoformat(),
                    "user": x.user,
                    "system": x.system,
                    "managed_object": x.managed_object,
                    "op": x.op,
                    "message": x.message
                }
                for x in o.get_log()
            ]
        }
