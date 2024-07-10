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

# Third-party modules
from mongoengine import ValidationError

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
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
from noc.core.inv.path import find_path
from noc.core.translation import ugettext as _

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
            container = request.GET["node"]
            if is_objectid(container):
                container = Object.get_by_id(container)
                if not container:
                    return self.response_not_found()
                children = [(o.name, o) for o in Object.objects.filter(container=container.id)]
                # Collect inner connections
                children += [(name, o) for name, o, _ in container.get_inner_connections()]
            elif container == "root":
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
                        __raw__={"container": None, "model": {"$in": cmodels}}
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
                "can_add": bool(o.get_data("container", "container")),
                "can_delete": str(o.model.uuid) not in self.UNDELETABLE,
            }
            plugins = []
            if o.get_data("container", "container") or o.has_inner_connections():
                # n["expanded"] = Object.objects.filter(container=o.id).count() == 1
                n["expanded"] = False
            else:
                n["leaf"] = True
            if o.model.front_facade or o.model.rear_facade:
                plugins.append(self.get_plugin_data("facade"))
            if o.get_data("rack", "units"):
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
            if o.get_data("container", "container"):
                plugins.append(self.get_plugin_data("sensor"))
            plugins.append(self.get_plugin_data("crossing"))
            # Process disabled plugins
            n["plugins"] = [p for p in plugins if p["name"] not in disabled_plugins]
            # Navigation glyphs
            icon_cls = o.model.glyph_css_class
            if icon_cls:
                n["iconCls"] = icon_cls
            r.append(n)
        return r

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
        o = Object(name=name, model=m, container=c)
        if serial and m.get_data("asset", "part_no0"):
            o.set_data("asset", "serial", serial)
        o.save()
        o.log("Created", user=request.user.username, system="WEB", op="CREATE")
        return str(o.id)

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
            cc = self.get_object_or_404(Object, id=c.container.id) if c.container else None
            for x in o:
                x.put_into(cc)
        return True

    @view("^(?P<id>[0-9a-f]{24})/path/$", method=["GET"], access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(Object, id=id)
        path = [{"id": str(o.id), "name": o.name}]
        while not o.container:
            # Check outer connections
            oc = next(o.iter_outer_connections(), None)
            if not oc:
                break
            o = oc[1]
            path.insert(0, {"id": str(o.id), "name": o.name})
        while o.container:
            o = o.container
            path.insert(0, {"id": str(o.id), "name": o.name})
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
        lo: Object = self.get_object_or_404(Object, id=o1)  # Left Object
        check: List[Tuple[str, Object, str, Optional[Object], Optional[str]]] = [
            ("left", lo, left_filter, None, None)
        ]
        ro: Optional[Object] = None  # Right Object
        cable: Optional[ObjectModel] = None
        if o2:
            ro = self.get_object_or_404(Object, id=o2)
            check = [
                ("left", lo, left_filter, ro, right_filter),
                ("right", ro, right_filter, lo, left_filter),
            ]
        if cable_filter:
            cable = ObjectModel.get_by_name(cable_filter)
        checking_ports = []
        id_ports_map = {}  # Left ports
        # Getting cable
        cables = ObjectModel.objects.filter(
            data__match={"interface": "length", "attr": "length", "value__gte": 0},
        )
        result = {
            "left": {"connections": [], "device": {}, "internal_connections": []},
            "right": {
                "connections": [],
                "device": {},
                "internal_connections": [],
            },
            "cable": [{"name": c.name, "available": True} for c in cables],
            "valid": False,
            "wires": [],
        }
        # Left and Right Object Processed
        for key, o_from, left_filter, o_to, right_filter in check:
            internal_used, left_cross = self.get_cross(o_from)

            result[key]["internal_connections"] = left_cross
            for c in o_from.model.connections:
                cid = f"{str(o_from.id)}{c.name}"
                id_ports_map[key, c.name] = cid
                c_data = o_from.get_effective_connection_data(c.name)
                oc, oo, _ = o_from.get_p2p_connection(c.name)
                self.logger.debug(
                    "[%s -> %s][%s] Checking connections: free: %s, valid: %s",
                    o_from,
                    o_to,
                    cid,
                    oc,
                    oo,
                )
                # Deny same and internal <-> external
                valid = not internal and c.type.name != "Composed"
                if left_filter == c.name and o_from == o1:
                    # Same connection
                    valid = False
                if o_to or cable_filter:
                    cp = o_from.get_connection_proposals(
                        c.name,
                        cable or o_to.model,
                        right_filter if not cable else None,
                        only_first=True,
                    )
                    valid = bool(cp)
                if oc and o_from == lo:
                    checking_ports.append(c)
                free = not oc
                r = {
                    "id": cid,
                    "name": c.name,
                    "type": str(c.type.id),
                    "type__label": c.type.name,
                    "gender": c.gender,
                    "direction": c.direction,
                    "protocols": [str(p) for p in c_data.protocols],
                    "free": free,
                    # "allow_internal": False,
                    "internal": None,
                    "valid": valid,
                    "disable_reason": "",
                }
                if o_from.model.has_connection_cross(c.name):
                    # Allowed crossed input
                    r["internal"] = {
                        "valid": c.name != left_filter and not (internal and left_filter),
                        "free": c.name not in internal_used,
                        "allow_discriminators": [],
                    }
                    if internal and left_filter:
                        rc = o_from.get_crossing_proposals(c.name, left_filter)
                        if rc:
                            r["internal"].update(
                                {"valid": True, "free": True, "allow_discriminators": rc[0][1]}
                            )
                if not free:
                    rd = self.get_remote_device(c.name, c_data.protocols, o_from)
                    if rd and rd.obj != o_to:
                        r["remote_device"] = {
                            "name": rd.obj.name,
                            "id": str(rd.obj.id),
                            "slot": rd.connection,
                        }
                result[key]["connections"] += [r]
            # lcs.append(r)
        if result["left"]["connections"] and result["right"]["connections"]:
            result["left"]["device"] = {"id": str(lo.id), "name": lo.name}
            result["right"]["device"] = {"id": str(ro.id), "name": ro.name}
            result["valid"] = left_filter and right_filter
            for p in checking_ports:
                cable, remote = self.get_remote_slot(p, lo, ro)
                if remote:
                    result["wires"].append(
                        [
                            {
                                "id": id_ports_map.get(("left", p.name), 0),
                                "name": p.name,
                                "side": "left",
                            },
                            {
                                "id": id_ports_map.get(("right", remote.connection), 0),
                                "name": remote.connection,
                                "side": "right",
                            },
                        ]
                    )
        return result
        # return {
        #     "left": {"connections": lcs, "device": device_left, "internal_connections": left_cross},
        #     "right": {
        #         "connections": rcs,
        #         "device": device_right,
        #         "internal_connections": right_cross,
        #     },
        #     "cable": [{"name": c.name, "available": True} for c in cables],
        #     "valid": lcs and rcs and left_filter and right_filter,
        #     "wires": wires,
        # }

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
                container=None,  # lo.container.id if lo.container else None,
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
        print(">>>", data)
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

    def get_remote_slot(self, left_slot, lo, ro):
        """
        Determine right device's slot with find_path method
        :return:
        """
        wire = None
        for path in (
            find_path(
                lo,
                left_slot.name,
                [str(p).translate(translation_map) for p in left_slot.protocols],
                trace_wire=True,
            )
            or []
        ):
            if path.obj.model.get_data("length", "length"):
                wire = path.obj
            if path.obj == ro:
                return wire, path
        return None, None

    def get_remote_device(self, slot, protocols, o):
        """
        Determing remote device with find_path method
        :return:
        """
        for path in (
            find_path(
                o, slot, [str(p).translate(translation_map) for p in protocols], trace_wire=True
            )
            or []
        ):
            if path.obj != o and not path.obj.is_wire:
                return path

    def get_cs_item(
        self,
        id,
        name,
        type,
        type__label,
        gender,
        direction,
        protocols,
        free,
        valid,
        disable_reason,
        o,
        internal_valid,
        internal_free,
    ):
        """
        Creating member of cs dict
        :return:
        """

        cs = {
            "id": id,
            "name": name,
            "type": type,
            "type__label": type__label,
            "gender": gender,
            "direction": direction,
            "protocols": protocols,
            "free": free,
            "allow_internal": bool(protocols),  # Allowed crossed input
            "internal": {
                "valid": internal_valid,
                "free": internal_free,
                "allow_discriminators": [],
            },
            "valid": valid,
            "disable_reason": disable_reason,
        }
        if not free:
            rd = self.get_remote_device(name, protocols, o)
            if rd:
                cs["remote_device"] = {
                    "name": rd.obj.name,
                    "id": str(rd.obj.id),
                    "slot": rd.connection,
                }
        return cs

    @staticmethod
    def format_discriminator(d) -> str:
        if not d:
            return d
        prefix, d = d.split("::", 1)
        if prefix == "lambda":
            return f"{chr(955)}{d}"
        return d

    def get_cross(self, o: Object) -> Tuple[Set[str], List[Dict[str, Any]]]:
        r, used = [], set()
        for s, ss in [("model", o.model), ("object", o)]:
            for c in ss.cross:
                r += [
                    {
                        "from": {
                            "id": f"{str(o.id)}{c.input}",
                            "name": c.input,
                            "has_arrow": False,
                            "discriminator": self.format_discriminator(c.input_discriminator or ""),
                        },
                        "to": {
                            "id": f"{str(o.id)}{c.output}",
                            "name": c.output,
                            "has_arrow": True,
                            "discriminator": self.format_discriminator(
                                c.output_discriminator or ""
                            ),
                        },
                        "gain_db": c.gain_db or 1.0,
                        "is_delete": s == "object",
                    }
                ]
                used |= {c.input, c.output}
        return used, r

    def can_show_topo(self, o: Object) -> bool:
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
        if any(o.iter_connections("o")):
            return True
        # Inside rack or PoP
        while o:
            if o.get_data("rack", "units"):
                return True
            if o.get_data("pop", "level") is not None:
                return True
            o = o.container
        return False

    @view(url=r"^(?P<oid>[0-9a-f]{24})/map_lookup/$", method=["GET"], access="read", api=True)
    def api_map_lookup(self, request, oid):
        o: Object = self.get_object_or_404(Object, id=oid)
        if not o.get_data("container", "container"):
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
