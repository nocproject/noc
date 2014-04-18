# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import inspect
import os
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.lib.validators import is_objectid
from noc.sa.interfaces.base import (StringParameter, ObjectIdParameter,
                                    UnicodeParameter, ListOfParameter)


class InvApplication(ExtApplication):
    """
    inv.inv application
    """
    title = "Inventory"
    menu = "Inventory"

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        # Load plugins
        from plugins.base import InvPlugin
        self.plugins = {}
        for f in os.listdir("inv/apps/inv/plugins/"):
            if (not f.endswith(".py") or
                    f == "base.py" or
                    f.startswith("_")):
                continue
            mn = "noc.inv.apps.inv.plugins.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (inspect.isclass(o) and
                        issubclass(o, InvPlugin) and
                        o.__module__.startswith(mn)):
                    assert o.name
                    self.plugins[o.name] = o(self)

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

    def get_plugin_data(self, name):
        return {
            "name": name,
            "xtype": self.plugins[name].js
        }

    @view("^node/$", method=["GET"],
          access="read", api=True)
    def api_node(self, request):
        container = None
        if request.GET and "node" in request.GET:
            container = request.GET["node"]
            if container == "root":
                container = self.get_root()
            elif not is_objectid(container):
                raise Exception("Invalid node")
            else:
                container = self.get_object_or_404(Object, id=container)
        r = []
        if not container:
            container = self.get_root()
        # Collect children objects
        children = [
            (o.name, o)
            for o in Object.objects.filter(container=container.id)
        ]
        # Collect inner connections
        children += [
            (name, o) for name, o, _ in container.get_inner_connections()
        ]
        # Build node interface
        for name, o in children:
            m_plugins = o.model.plugins or []
            disabled_plugins = set(p[1:] for p in m_plugins if p.startswith("-"))
            n = {
                "id": str(o.id),
                "name": name,
                "plugins": [],
                "can_add": bool(o.get_data("container", "container"))
            }
            if (o.get_data("container", "container") or
                    o.has_inner_connections()):
                n["expanded"] = Object.objects.filter(container=o.id).count() == 1
            else:
                n["leaf"] = True
            if o.get_data("rack", "units"):
                n["plugins"] += [self.get_plugin_data("rack")]
            if o.model.connections:
                n["plugins"] += [self.get_plugin_data("inventory")]
            if o.get_data("geopoint", "layer"):
                n["plugins"] += [self.get_plugin_data("map")]
            if o.get_data("management", "managed_object"):
                n["plugins"] += [self.get_plugin_data("managedobject")]
            # Append model's plugins
            for p in m_plugins:
                if not p.startswith("-"):
                    n["plugins"] += [self.get_plugin_data(p)]
            n["plugins"] += [
                self.get_plugin_data("data"),
                self.get_plugin_data("comment"),
                self.get_plugin_data("file"),
                self.get_plugin_data("log")
            ]
            # Process disabled plugins
            n["plugins"] = [p for p in n["plugins"] if p["name"] not in disabled_plugins]
            r += [n]
        return r

    @view("^add_group/$", method=["POST"], access="create_group",
          api=True,
          validate={
              "container": ObjectIdParameter(required=False),
              "type": ObjectIdParameter(),
              "name": UnicodeParameter(),
              "serial": UnicodeParameter(required=False)
          })
    def api_add_group(self, request, type, name, container=None,
                      serial=None):
        if container is None:
            c = self.get_root()
        else:
            c = self.get_object_or_404(Object, id=container)
        m = self.get_object_or_404(ObjectModel, id=type)
        o = Object(name=name, model=m, container=c.id)
        if serial and m.get_data("asset", "part_no0"):
            o.set_data("asset", "serial", serial)
        o.save()
        o.log("Created", user=request.user.username,
              system="WEB", op="CREATE")
        return str(o.id)

    @view("^remove_group/$", method=["DELETE"], access="remove_group",
          api=True,
          validate={
              "container": ObjectIdParameter(required=True)
          })
    def api_remove_group(self, request, container=None):
        c = self.get_object_or_404(Object, id=container)
        c.delete()
        return True

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
        elif position in ("before", "after"):
            cc = self.get_object_or_404(Object, id=c.container)
            for x in o:
                x.put_into(cc)
        return True

    @view("^(?P<id>[0-9a-f]{24})/path/$", method=["GET"],
          access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(Object, id=id)
        path = [{
            "id": str(o.id),
            "name": o.name
        }]
        root = self.get_root().id
        while o.container and o.container != root:
            o = Object.objects.get(id=o.container)
            path = [{
                "id": str(o.id),
                "name": o.name
            }] + path
        return path