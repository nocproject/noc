# ---------------------------------------------------------------------
# inv.inv application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import inspect
import operator
import os
import threading
from typing import Optional, Dict, List, Any, Tuple, Iterable
from collections import defaultdict


# Third-party modules
import cachetools
from mongoengine import ValidationError

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.inv.models.object import Object
from noc.inv.models.error import ConnectionError
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.configuredmap import ConfiguredMap
from noc.inv.models.sensor import Sensor
from noc.core.validators import is_objectid
from noc.core.inv.result import Result
from noc.core.inv.attach.container import attach as attach_to_container
from noc.core.inv.attach.rack import (
    attach as attach_to_rack,
    RackPosition,
    RackSide,
    iter_choices as iter_rack_choices,
)
from noc.core.inv.attach.module import (
    attach as attach_module,
    ModulePosition,
    get_free as get_free_for_module,
)
from noc.core.inv.info import info
from noc.core.inv.clone import clone
from noc.core.inv.remove import remote_all, remove_root, remove_connections
from noc.sa.interfaces.base import (
    StringParameter,
    ObjectIdParameter,
    UnicodeParameter,
    ListOfParameter,
    BooleanParameter,
    DictListParameter,
    DictParameter,
    FloatParameter,
)
from noc.core.translation import ugettext as _
from noc.core.text import alnum_key
from .pbuilder import CrossingProposalsBuilder

id_lock = threading.Lock()
translation_map = str.maketrans("<>", "><")


class InvApplication(ExtApplication):
    """
    inv.inv application
    """

    title = _("Inventory")
    menu = _("Inventory")
    glyph = "archive"

    # Undeletable nodes
    UNDELETABLE = {
        # Global Lost&Found
        "b0fae773-b214-4edf-be35-3468b53b03f2"
    }
    _id_cache = cachetools.TTLCache(1000, ttl=60)

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        # Load plugins
        from .plugins.base import InvPlugin

        self.plugins = {}
        for f in os.listdir("services/web/apps/inv/inv/plugins/"):
            if not f.endswith(".py") or f == "base.py" or f.startswith("_"):
                continue
            mn = "noc.services.web.apps.inv.inv.plugins.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if inspect.isclass(o) and issubclass(o, InvPlugin) and o.__module__.startswith(mn):
                    assert o.name
                    self.plugins[o.name] = o(self)

    def get_plugin_data(self, name):
        return {"name": name, "xtype": self.plugins[name].js}

    @view("^node/$", method=["GET"], access="read", api=True)
    def api_node(self, request):
        children = []
        if request.GET and "node" in request.GET:
            parent = request.GET["node"]
            if is_objectid(parent):
                parent = Object.get_by_id(parent)
                if not parent:
                    return self.response_not_found()
                if parent.is_container:
                    # Sort by alnum key
                    sort_key = lambda x: alnum_key(x.name or "")
                else:
                    # Sort by parent's model
                    conn_rank = {conn.name: n for n, conn in enumerate(parent.model.connections)}
                    sort_key = lambda x: conn_rank.get(x.parent_connection, 999)
                children = [
                    (
                        (
                            f"{o.parent_connection} [{o.model.get_short_label()}]"
                            if o.parent_connection
                            else o.name
                        ),
                        o,
                    )
                    for o in sorted(parent.iter_children(), key=sort_key)
                ]
            elif parent == "root":
                cmodels = [
                    d["_id"]
                    for d in ObjectModel._get_collection().find(
                        {
                            "data": {
                                "$elemMatch": {
                                    "interface": "container",
                                    "attr": "container",
                                    "value": True,
                                }
                            }
                        },
                        {"_id": 1},
                    )
                ]
                children: List[Tuple[str, "Object"]] = [
                    (o.name, o)
                    for o in Object.objects.filter(
                        __raw__={"parent": None, "model": {"$in": cmodels}}
                    )
                ]

            else:
                return self.response_bad_request()
        r = []
        # Build node interface
        for name, o in children:
            m_plugins = o.model.plugins or []
            disabled_plugins = set(p[1:] for p in m_plugins if p.startswith("-"))
            n = {
                "id": str(o.id),
                "name": name,
                "plugins": [],
                "can_add": o.is_container,
                "can_delete": str(o.model.uuid) not in self.UNDELETABLE,
            }
            plugins = []
            if o.is_container or o.has_children:
                # n["expanded"] = Object.objects.filter(container=o.id).count() == 1
                n["expanded"] = False
            else:
                n["leaf"] = True
            if o.model.front_facade or o.model.rear_facade:
                plugins.append(self.get_plugin_data("facade"))
            if o.is_rack:
                plugins.append(self.get_plugin_data("rack"))
            if o.model.connections:
                plugins.append(self.get_plugin_data("inventory"))
            if o.get_data("geopoint", "layer"):
                plugins.append(self.get_plugin_data("map"))
            if o.get_data("contacts", "has_contacts"):
                plugins.append(self.get_plugin_data("contacts"))
            if self.can_show_topo(o):
                plugins.append(self.get_plugin_data("channel"))
                plugins.append(self.get_plugin_data("commutation"))
                plugins.append(self.get_plugin_data("bom"))
                plugins.append(self.get_plugin_data("job"))
            if o.model.cross or o.cross or o.get_data("caps", "dynamic_crossing"):
                plugins.append(self.get_plugin_data("crossing"))
            if o.model.sensors or Sensor.objects.filter(object=o.id).first():
                plugins.append(self.get_plugin_data("sensor"))
                plugins.append(self.get_plugin_data("metric"))
            if o.model.configuration_rule:
                plugins.append(self.get_plugin_data("param"))
            # Append model's plugins
            plugins += [self.get_plugin_data(p) for p in m_plugins if not p.startswith("-")]
            # Common plugins
            plugins += [
                self.get_plugin_data("data"),
                self.get_plugin_data("comment"),
                self.get_plugin_data("file"),
                self.get_plugin_data("log"),
            ]
            if o.is_container:
                plugins.append(self.get_plugin_data("sensor"))
            # Process disabled plugins
            n["plugins"] = [p for p in plugins if p["name"] not in disabled_plugins]
            # Navigation glyphs
            icon_cls = o.model.glyph_css_class
            if icon_cls:
                n["iconCls"] = icon_cls
            r.append(n)
        return r

    @view(
        "^attach/$",
        method=["POST"],
        access="create_group",
        api=True,
        validate={
            "container": ObjectIdParameter(),
            "item": ObjectIdParameter(),
            "choice": StringParameter(required=False),
        },
    )
    def api_attach(self, request, container: str, item: str, choice: Optional[str] = None):
        # Resolve items
        c_obj = self.get_object_or_404(Object, id=container)
        i_obj = self.get_object_or_404(Object, id=item)
        if c_obj.is_rack and i_obj.is_rackmount and not (choice and choice == "---"):
            return self._attach_rack(c_obj, i_obj, choice=choice)
        if c_obj.is_container:
            return attach_to_container(c_obj, i_obj).as_response()
        if any(True for cn in c_obj.model.connections if cn.is_inner):
            return self._attach_inner(c_obj, i_obj, choice=choice)
        return Result(status=False, message="Cannot be connected").as_response()

    def _attach_rack(self, container: Object, item: Object, choice: str | None):
        """Insert item to rack"""
        if choice:
            try:
                pos = RackPosition.from_str(choice)
            except ValueError:
                return Result(status=False, message="Invalid position").as_response()
            return attach_to_rack(container, item, position=pos).as_response()
        # Generate free list
        children = [{"id": "---", "name": "Put into", "iconCls": "fa fa-download", "leaf": True}]
        free: defaultdict[RackSide, list[int]] = defaultdict(list)
        for pos in iter_rack_choices(container, item):
            free[pos.side].append(pos.position)
        # Front
        if RackSide.FRONT in free:
            children.append(
                {
                    "name": "Front",
                    "iconCls": "fa fa-hand-o-right",
                    "children": [
                        {"id": f"f-{n}", "name": str(n), "leaf": True}
                        for n in sorted(free[RackSide.FRONT], reverse=True)
                    ],
                    "expanded": True,
                }
            )
        # Rear
        if RackSide.REAR in free:
            children.append(
                {
                    "name": "Rear",
                    "iconCls": "fa fa-hand-o-left",
                    "children": [
                        {"id": f"r-{n}", "name": str(n), "leaf": True}
                        for n in sorted(free[RackSide.REAR], reverse=True)
                    ],
                    "expanded": True,
                }
            )
        return {"choices": {"children": children, "expanded": True}}

    def _attach_inner(self, container: Object, item: Object, choice: Optional[str] = None):
        """Insert item into chassis/module."""

        def to_tree(iter: Iterable[ModulePosition]) -> dict[str, Any] | None:
            def from_obj(obj: Object) -> dict[str, Any]:
                if obj.parent_connection:
                    label = f"{obj.parent_connection} [{obj.model.get_short_label()}]"
                else:
                    label = obj.model.get_short_label()
                # Prepare Node
                return {"iconCls": obj.model.glyph_css_class, "name": label}

            def prepare_children(item: dict[str, Any]) -> None:
                if "children" not in item:
                    item["expanded"] = True
                    item["children"] = []

            def build_hierarchy(obj: Object) -> None:
                if not obj.parent:
                    return
                if obj.parent != container:
                    build_hierarchy(obj.parent)
                prepare_children(items[obj.parent])
                items[obj.parent]["children"].append(items[obj])

            items: dict[Object, dict[str, Any]] = {container: from_obj(container)}
            # Consume iterator
            for pos in iter:
                if pos.obj not in items:
                    items[pos.obj] = from_obj(pos.obj)
                    build_hierarchy(pos.obj)
                current = items[pos.obj]
                prepare_children(current)
                current["children"].append(
                    {"id": pos.as_resource(), "name": pos.name, "leaf": True}
                )
            if "children" in items[container]:
                return items[container]
            return None

        outer = item.model.get_outer()
        if not outer:
            return Result(status=False, message="Cannot connnect").as_response()
        if choice:
            pos = ModulePosition.from_resource(choice)
            if pos is None:
                return Result(status=False, message="Not found").as_response()
            return attach_module(item, position=pos).as_response()
        # Build choices
        r = to_tree(get_free_for_module(container, item))
        if r:
            return {"choices": {"children": [r], "expanded": True}}
        return Result(status=False, message="Cannot connect").as_response()

    @view(
        "^add_group/$",
        method=["POST"],
        access="create_group",
        api=True,
        validate={
            "container": ObjectIdParameter(required=False),
            "type": ObjectIdParameter(),
            "name": UnicodeParameter(),
            "serial": UnicodeParameter(required=False),
        },
    )
    def api_add_group(self, request, type, name, container=None, serial=None):
        if is_objectid(container):
            c = Object.get_by_id(container)
            if not c:
                return self.response_not_found()
            c = c.id
        elif container:
            return self.response_bad_request()
        else:
            c = None
        m = ObjectModel.get_by_id(type)
        if not m:
            return self.response_not_found()
        o = Object(name=name, model=m, parent=c)
        if serial and m.get_data("asset", "part_no0"):
            o.set_data("asset", "serial", serial)
        o.save()
        o.log("Created", user=request.user.username, system="WEB", op="CREATE")
        return str(o.id)

    @view(
        "^add/$",
        method=["POST"],
        access="create_group",
        api=True,
        validate={
            "container": ObjectIdParameter(required=False),
            "items": DictListParameter(
                attrs={
                    "model": ObjectIdParameter(),
                    "name": UnicodeParameter(),
                    "serial": UnicodeParameter(required=False),
                }
            ),
        },
    )
    def api_add(self, request, items: List[Dict[str, str]], container: Optional[str] = None):
        if container:
            parent = self.get_object_or_404(Object, id=container)
        else:
            parent = None
        for item in items:
            model = self.get_object_or_404(ObjectModel, id=item["model"])
            obj = Object(name=item["name"], model=model, parent=parent)
            serial = item.get("serial")
            if serial and model.get_data("asset", "part_no0"):
                obj.set_data("asset", "serial", serial)
            obj.save()
            obj.log("Created", user=request.user.username, system="WEB", op="CREATE")
        return {"status": True}

    @view(
        "^remove_group/$",
        method=["DELETE"],
        access="remove_group",
        api=True,
        validate={
            "container": ObjectIdParameter(required=True),
            "action": StringParameter(choices=["p", "l", "r"]),
            "keep_connections": BooleanParameter(required=False),
        },
    )
    def api_remove_group(
        self, request, container: str, action: str, keep_connections: bool = False
    ):
        obj = self.get_object_or_404(Object, id=container)
        match action:
            case "p":
                n = remove_root(obj, obj.get_container(), keep_connections=keep_connections)
            case "l":
                n = 0
            case "r":
                n = remote_all(obj)
            case _:
                raise NotImplementedError
        return {"status": True, "message": f"{n} objects deleted"}

    @view(
        "^remove_connections/$",
        method=["DELETE"],
        access="remove_group",
        api=True,
        validate={
            "container": ObjectIdParameter(required=True),
        },
    )
    def api_remove_connections(self, request, container: str):
        obj = self.get_object_or_404(Object, id=container)
        remove_connections(obj)
        return {"status": True, "message": "Conections cleared"}

    @view(
        "^insert/$",
        method=["POST"],
        access="reorder",
        api=True,
        validate={
            "container": ObjectIdParameter(required=False),
            "objects": ListOfParameter(element=ObjectIdParameter()),
            "position": StringParameter(),
        },
    )
    def api_insert(self, request, container, objects, position):
        """
        :param request:
        :param container: ObjectID after/in that insert
        :param objects: List ObjectID for insert
        :param position: 'append', 'before', 'after'
        :return:
        """
        c = self.get_object_or_404(Object, id=container)
        o = []
        for r in objects:
            o += [self.get_object_or_404(Object, id=r)]
        if position == "append":
            for x in o:
                x.put_into(c)
        elif position in ("before", "after"):
            cc = self.get_object_or_404(Object, id=c.parent.id) if c.parent else None
            for x in o:
                x.put_into(cc)
        return True

    @view("^(?P<id>[0-9a-f]{24})/path/$", method=["GET"], access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(Object, id=id)
        path = [{"id": str(o.id), "name": o.name}]
        while o.parent:
            o = o.parent
            path.insert(
                0, {"id": str(o.id), "name": o.parent_connection if o.parent_connection else o.name}
            )
        return path

    @view(
        "^crossing_proposals/$",
        method=["GET"],
        access="read",
        api=True,
        validate={
            "o1": ObjectIdParameter(required=True),
            "o2": ObjectIdParameter(required=False),
            "left_filter": UnicodeParameter(required=False),
            "right_filter": UnicodeParameter(required=False),
            "cable_filter": UnicodeParameter(required=False),
            "internal": BooleanParameter(default=False),
        },
    )
    def api_get_crossing_proposals(
        self,
        request,
        o1: str,
        o2: str | None = None,
        left_filter: Optional[str] = None,
        right_filter: Optional[str] = None,
        cable_filter: Optional[str] = None,
        internal: bool = False,
    ):
        """
        API for connection form. Checked proposals object connection
        For internal flag - check crossing
        Denied connections:
           * internal and external pin
           * Same pin
        :param request:
        :param o1: From object
        :param o2: To Object
        :param left_filter: From object connection pin
        :param right_filter: To object connection pin
        :param cable_filter: Used cable for connection
        :param internal: For internal connection (crossing)
        :return: Connection and status:
            * Free - pin with exists connection on pin
            * Valid - pin may be used for connection
        """
        self.logger.info(
            "Crossing proposals: %s:%s -> %s:%s (Cable: %s, Internal: %s)",
            o1,
            left_filter,
            o2,
            right_filter,
            cable_filter,
            internal,
        )
        lo = self.get_object_or_404(Object, id=o1)  # Left Object
        ro = self.get_object_or_404(Object, id=o2) if o2 else None  # Right object
        builder = CrossingProposalsBuilder(
            lo=lo,
            ro=ro,
            left_filter=left_filter,
            right_filter=right_filter,
            internal=internal,
            cable_filter=cable_filter,
        )
        return builder.build()

    @view(
        "^connect/$",
        method=["POST"],
        access="connect",
        api=True,
        validate=DictListParameter(
            attrs={
                "object": ObjectIdParameter(required=True),
                "name": StringParameter(required=True),
                "remote_object": ObjectIdParameter(required=False),
                "remote_name": StringParameter(required=True),
                # "cable": ObjectIdParameter(required=False),
                "cable": StringParameter(required=False),
                "reconnect": BooleanParameter(default=False, required=False),
                "is_internal": BooleanParameter(default=False, required=False),
                "discriminator": DictParameter(
                    attrs={"input": StringParameter(), "output": StringParameter()},
                    required=False,
                ),
                "gain_db": FloatParameter(required=False),
            }
        ),
    )
    def api_connect(
        self,
        request,
        **kwargs,
    ):
        def register_error(link: Dict[str, Any], err: str) -> None:
            self.logger.warning("Connection Error: %s", err)
            link["error"] = err
            errors.append(link)

        def create_internal_connection(link: Dict[str, Any]) -> None:
            name, remote_name = link["name"], link["remote_name"]
            try:
                discriminator = link.get("discriminator") or {}
                lo.set_internal_connection(
                    name,
                    remote_name,
                    data={
                        "gain_db": link.get("gain_db") or 1.0,
                        "input_discriminator": discriminator.get("input"),
                        "output_discriminator": discriminator.get("output"),
                    },
                )
                lo.save()
            except (ConnectionError, ValidationError) as e:
                register_error(link, str(e))

        def create_cable_connection(link: Dict[str, Any], lo: Object, ro: Object) -> None:
            cable_model = ObjectModel.get_by_name(link["cable"])
            if not cable_model:
                register_error(link, f"Invalid cable model: {link['cable']}")
                return
            name, remote_name = link["name"], link["remote_name"]
            cable = Object(
                name=f"Wire {lo.name}:{name} <-> {ro.name}:{remote_name}",
                model=cable_model,
                parent=None,
            )
            cable.save()
            # Connect to cable
            c1, c2 = cable.model.connections[:2]
            self.logger.debug("Wired connect %s:%s", c1, c2)
            reconnect = link.get("reconnect")
            name, remote_name = link["name"], link["remote_name"]
            try:
                lo.connect_p2p(name, cable, c1.name, {}, reconnect=reconnect)
                ro.connect_p2p(remote_name, cable, c2.name, {}, reconnect=reconnect)
                lo.save()
                ro.save()
            except ConnectionError as e:
                register_error(link, str(e))

        def create_p2p_connection(link: Dict[str, Any], lo: Object, ro: Object) -> None:
            name, remote_name = link["name"], link["remote_name"]
            try:
                lo.connect_p2p(name, ro, remote_name, {}, reconnect=link.get("reconnect"))
            except ConnectionError as e:
                register_error(link, str(e))

        data: List[Dict[str, Any]] = self.deserialize(request.body)
        errors: List[Dict[str, Any]] = []
        for link in data:
            lo = self.get_object_or_404(Object, id=link["object"])
            remote_object = link.get("remote_object")
            if link.get("is_internal"):
                create_internal_connection(link)
                continue
            if remote_object:
                # Connect to the remote object
                ro = self.get_object_or_404(Object, id=remote_object)
            elif link["name"] == link["remote_name"]:
                register_error(link, "Circular connection to same slot is not allowed")
                continue
            else:
                # Connect the same object
                ro = lo
            if link.get("cable"):
                create_cable_connection(link, lo, ro)
            else:
                create_p2p_connection(link, lo, ro)
        # Check for errors
        if errors:
            return self.render_json(
                {"status": False, "text": "Invalid connections", "invalid_connections": errors}
            )
        return self.render_json({"status": True, "text": ""})

    @view(
        "^disconnect/$",
        method=["POST"],
        access="connect",
        api=True,
        validate={
            "object": ObjectIdParameter(required=True),
            "name": StringParameter(required=True),
            "remote_object": ObjectIdParameter(required=False),
            "remote_name": StringParameter(required=True),
            "is_internal": BooleanParameter(default=False, required=False),
        },
    )
    def api_disconnect(
        self,
        request,
        object,
        name,
        remote_name,
        remote_object: Optional[str] = None,
        is_internal: bool = False,
    ):
        lo: Object = self.get_object_or_404(Object, id=object)
        if is_internal:
            # Cross-connect
            lo.disconnect_internal(name, remote_name)
        else:
            ro: Object = self.get_object_or_404(Object, id=remote_object)
            lo.disconnect_p2p(name)
            ro.disconnect_p2p(remote_name)  # Unnecessary for cables
        lo.save()
        return self.render_json({"status": True, "text": ""})

    @staticmethod
    def can_show_topo(o: Object) -> bool:
        """
        Check if topology-related and channel plugins
        can be used.

        Args:
            o: Object instance

        Returns:
            True: if topology-related plugins can be used.
            False: Otherwise.
        """
        # Is chassis
        if o.model.cr_context == "CHASSIS":
            return True
        # Has outer connections
        if o.parent_connection:
            return True
        # Inside rack or PoP
        while o:
            # Sandbox
            if o.model.name == "Sandbox":
                return True
            # Rack
            if o.is_rack:
                return True
            # PoP
            if o.is_pop:
                return True
            o = o.parent
        return False

    @view(url=r"^(?P<oid>[0-9a-f]{24})/map_lookup/$", method=["GET"], access="read", api=True)
    def api_map_lookup(self, request, oid):
        o: Object = self.get_object_or_404(Object, id=oid)
        if not o.is_container:
            return []
        r = [
            {
                "id": str(o.id),
                "label": _("ManagedObject Container: ") + str(o.name),
                "is_default": True,
                "args": ["objectcontainer", str(o.id), str(o.id)],
            }
        ]
        for cm in ConfiguredMap.objects.filter(nodes__object_filter__container=oid):
            r += [
                {
                    "id": str(cm.id),
                    "label": _("Configured Map Container: ") + str(o.name),
                    "is_default": False,
                    "args": ["configured", str(cm.id)],
                }
            ]
        return r

    @view(
        "^clone/$",
        method=["POST"],
        access="create_group",
        api=True,
        validate=DictParameter(
            attrs={
                "container": ObjectIdParameter(required=True),
                "clone_connections": StringParameter(required=True),
            }
        ),
    )
    def api_clone(
        self,
        request,
        container: str,
        clone_connections: bool,
    ):
        obj = self.get_object_or_404(Object, id=container)
        cloned = clone(obj, clone_connections=clone_connections)
        return {"status": True, "object": str(cloned.id), "message": "Object cloned successfully"}

    @view(
        "^baloon/",
        method=["POST"],
        access="read",
        api=True,
        validate=DictParameter(attrs={"resource": StringParameter(required=True)}),
    )
    def api_baloon(self, request, resource: str):
        try:
            i = info(resource)
        except ValueError:
            return self.response_not_found()
        if not i:
            return self.response_not_found()
        return i.to_json()

    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_cable_ids(self):
        """
        Get cable IDs from ObjectModel
        """
        ids = ObjectModel.objects.filter(
            __raw__={
                "data": {
                    "$elemMatch": {
                        "interface": {"$eq": "length"},
                        "attr": {"$eq": "length"},
                    }
                },
            }
        ).values_list("id")
        return [id for id in ids]

    @view(
        "^search/$",
        method=["GET"],
        access="read",
        api=True,
        validate={"q": UnicodeParameter(required=True)},
    )
    def api_search(self, request, q: str, **kwargs):
        def path(o: Object) -> List[Dict]:
            result = []
            for oid in o.get_path():
                obj = Object.get_by_id(oid)
                connection = obj.connections[0] if obj.connections else None
                result += [
                    {
                        "id": str(oid),
                        "label": obj.name,
                        "connection": connection,
                    }
                ]
            return result

        start = kwargs.get("__start")
        limit = kwargs.get("__limit")
        query = {
            "$or": [
                {"name": {"$regex": q}},
                {
                    "data": {
                        "$elemMatch": {
                            "interface": {"$eq": "asset"},
                            "attr": {"$eq": "serial"},
                            "value": {"$regex": q},
                        }
                    },
                },
                {
                    "data": {
                        "$elemMatch": {
                            "interface": {"$eq": "asset"},
                            "attr": {"$eq": "part_no"},
                            "value": {"$regex": q},
                        }
                    },
                },
            ]
        }
        objs = Object.objects.filter(__raw__=query, model__nin=self.get_cable_ids()).order_by(
            "name"
        )
        start = int(start) if start is not None else 0
        limit = int(limit) if limit is not None else 1000
        objs = objs[start : start + limit]
        return {"status": True, "items": [{"path": path(o)} for o in objs]}
