# ---------------------------------------------------------------------
# inv.inv application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import inspect
import os
from typing import Optional, Dict, List, Any, Tuple, Set
import math

# Third-party modules
from mongoengine import ValidationError

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.core.resource import from_resource
from noc.inv.models.object import Object
from noc.inv.models.error import ConnectionError
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.configuredmap import ConfiguredMap
from noc.inv.models.sensor import Sensor
from noc.core.validators import is_objectid
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
from .pbuilder import CrossingProposalsBuilder
from .utils.clone import clone

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
                children = [
                    (
                        (
                            f"{o.parent_connection} [{o.model.get_short_label()}]"
                            if o.parent_connection
                            else o.name
                        ),
                        o,
                    )
                    for o in parent.iter_children()
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
            if o.get_data("management", "managed_object"):
                plugins.append(self.get_plugin_data("managedobject"))
            if o.get_data("contacts", "has_contacts"):
                plugins.append(self.get_plugin_data("contacts"))
            if self.can_show_topo(o):
                plugins.append(self.get_plugin_data("channel"))
                plugins.append(self.get_plugin_data("commutation"))
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
        c_obj = self.get_object_or_404(Object, id=container)
        i_obj = self.get_object_or_404(Object, id=item)
        if c_obj.is_rack and i_obj.is_rackmount and not (choice and choice == "---"):
            return self._attach_rack(c_obj, i_obj, choice=choice)
        if c_obj.is_container:
            return self._attach_container(c_obj, i_obj, choice=choice)
        if any(True for cn in c_obj.model.connections if cn.is_inner):
            return self._attach_inner(c_obj, i_obj, choice=choice)
        return self.render_json(
            {"status": False, "message": "Selected objects cannot be connected"}, status=400
        )

    def _attach_rack(self, container: Object, item: Object, choice: Optional[str] = None):
        """Insert item into rack."""

        def attach():
            # Check choice
            try:
                side, pos = choice.split("-")
                pos = int(pos)
            except ValueError:
                return self.render_json({"status": False, "message": "Invalid position"})
            # Check side
            if side not in ("f", "r"):
                return self.render_json({"status": False, "message": "Invalid side"})
            # Get free units
            free = get_side_free_units(side)
            # Get occupied units
            units = math.ceil(item.get_data("rackmount", "units"))
            occupied = set(range(pos, pos + units + 1))
            if not occupied.issubset(free):
                return self.render_json({"status": False, "message": "Space is busy"})
            # Attach to rack
            item.parent = container
            item.parent_connection = None
            # Set position
            item.set_data("rackmount", "position", pos)
            item.set_data("rackmount", "side", side)
            item.save()
            return self.render_json({"status": True, "message": "Placed to rack"}, status=200)

        def get_occupied_units(obj: Object) -> Optional[Set[int]]:
            """Get units occupied by object."""
            #  Get position
            o_pos = obj.get_data("rackmount", "position")
            if not o_pos:
                return None
            # Get size in units
            units = obj.get_data("rackmount", "units")
            if not units:
                return None
            has_shift = bool(obj.get_data("rackmount", "shift"))
            # Top position
            top = o_pos + math.ceil(units)
            if has_shift:
                top += 1
            # Mark as occupied
            return set(range(o_pos, top + 1))

        def get_side_free_units(side: str) -> Set[int]:
            free = set(range(1, container.get_data("rack", "units") + 1))
            # Process nested items
            for obj in container.iter_children():
                # Check side
                o_side = obj.get_data("rackmount", "side")
                if not o_side or o_side != side:
                    continue
                # Occupied units
                occupied = get_occupied_units(obj)
                if occupied:
                    free -= occupied
            return free

        def get_adjanced_available(free: Set[int]) -> Set[int]:
            """
            Return only units which have at least `units` free space above.
            """
            units = math.ceil(item.get_data("rackmount", "units"))
            r: Set[int] = set()
            for u in free:
                for nu in range(u, u + units):
                    if nu not in free:
                        break
                else:
                    r.add(u)
            return r

        def get_choices():
            def get_side_items(side: str) -> List[Dict[str, Any]]:
                # Generate items
                return [
                    {"id": f"{side}-{n}", "name": str(n), "leaf": True}
                    for n in sorted(get_adjanced_available(get_side_free_units(side)), reverse=True)
                ]

            children = [
                {"id": "---", "name": "Put into", "iconCls": "fa fa-download", "leaf": True}
            ]
            front_items = get_side_items("f")
            if front_items:
                children.append(
                    {
                        "name": "Front",
                        "iconCls": "fa fa-hand-o-right",
                        "children": front_items,
                        "expanded": True,
                    }
                )
            rear_items = get_side_items("r")
            if rear_items:
                children.append(
                    {
                        "name": "Rear",
                        "iconCls": "fa fa-hand-o-left",
                        "children": rear_items,
                        "expanded": True,
                    }
                )

            return {"children": children, "expanded": True}

        if choice:
            return attach()
        return {"choices": get_choices()}

    def _attach_container(self, container: Object, item: Object, choice: Optional[str] = None):
        """Insert item into container."""
        item.put_into(container)
        return {
            "status": True,
            "message": "Item have been moved",
        }

    def _attach_inner(self, container: Object, item: Object, choice: Optional[str] = None):
        """Insert item into chassis/module."""

        def attach():
            # Dereference
            obj: Object
            obj, name = from_resource(choice)
            if not obj:
                return self.render_json({"status": False, "message": "Not found"}, status=400)
            # Attach
            try:
                item.attach(obj, name)
            except ConnectionError as e:
                return self.render_json({"status": False, "message": str(e)}, status=400)
            return self.render_json({"status": True, "message": "Placed to rack"}, status=200)

        def get_free(obj: Object) -> Optional[Dict[str, Any]]:
            # Label
            if obj.parent_connection:
                label = f"{obj.parent_connection} [{obj.model.get_short_label()}]"
            else:
                label = obj.model.get_short_label()
            # Prepare Node
            r = {"iconCls": obj.model.glyph_css_class, "name": label}
            # Get used slots
            used_slots = set(obj.iter_used_connections())
            # Oversized?
            size = item.occupied_slots
            # Add slots
            c_data = []
            for cn in obj.model.connections:
                if not cn.is_inner or cn.name in used_slots:
                    continue
                # Check compatibility
                is_compatible, _ = ObjectModel.check_connection(cn, outer)
                if not is_compatible:
                    continue
                # Process oversized modules
                if size > 1:
                    next_conns = set(
                        cn.name for cn in obj.model.iter_next_connections(cn.name, size - 1)
                    )
                    if len(next_conns) != size - 1 or next_conns.intersection(used_slots):
                        continue
                # Add candidate
                c_data.append({"id": f"o:{obj.id}:{cn.name}", "name": cn.name, "leaf": True})
            # Process children
            for child in obj.iter_children():
                cf = get_free(child)
                if cf:
                    c_data.append(cf)
            # Finalize
            if c_data:
                r["expanded"] = True
                r["children"] = c_data
                return r
            return None

        outer = item.model.get_outer()
        if not outer:
            return self.render_json({"status": False, "message": "Cannot connect"}, status=400)
        if choice:
            return attach()
        # Build choices
        r = get_free(container)
        if r:
            return {"choices": {"children": [r], "expanded": True}}
        return self.render_json({"status": False, "message": "Cannot connect"}, status=400)

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
        validate={"container": ObjectIdParameter(required=True)},
    )
    def api_remove_group(self, request, container=None):
        c = self.get_object_or_404(Object, id=container)
        c.delete()
        return True

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
        o1,
        o2=None,
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
            ro.disconnect_p2p(remote_name)
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
