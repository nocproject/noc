# ---------------------------------------------------------------------
# inv.inv data plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Tuple, List, Optional, Iterable, Any
from collections import defaultdict
import math

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.modelinterface import ModelInterface
from noc.sa.interfaces.base import StringParameter
from noc.sa.models.managedobject import ManagedObject
from .base import InvPlugin


class DataPlugin(InvPlugin):
    name = "data"
    js = "NOC.inv.inv.plugins.data.DataPanel"

    RGROUPS = [
        [
            "Building",
            "PoP | International",
            "PoP | National",
            "PoP | Regional",
            "PoP | Core",
            "PoP | Aggregation",
            "PoP | Access",
        ]
    ]

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_save_data" % self.name,
            self.api_save_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/data/$",
            method=["PUT"],
            validate={
                "interface": StringParameter(),
                "key": StringParameter(),
                "value": StringParameter(default="", required=False),
            },
        )

    def get_data(self, request, o: Object):
        data = []
        data.extend(self.iter_common(o))
        if self.app.can_show_topo(o):
            data.extend(self.iter_summary(o))
        data.extend(self.iter_effective_data(o))
        return {"id": str(o.id), "name": o.name, "model": o.model.name, "data": data}

    @classmethod
    def item(
        cls,
        interface: str,
        name: str,
        value: str,
        description: str,
        required: bool = True,
        is_const: bool = False,
        type: Optional[str] = None,
        scope: Optional[str] = None,
        choices: Optional[List[Tuple[str, str]]] = None,
        item_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate item.
        """
        r = {
            "interface": interface,
            "name": name,
            "value": value,
            "description": description,
            "required": required,
            "is_const": is_const,
            "type": type,
        }
        if type:
            r["type"] = type
        if scope:
            r["scope"] = scope
        if choices is not None:
            r["choices"] = choices
        if item_id:
            r["item_id"] = item_id
        return r

    def iter_common(self, o: Object) -> Iterable[Dict[str, Any]]:
        interface = "Common"
        # Name
        yield self.item(
            interface=interface,
            name="Name",
            value=" | ".join(o.get_name_path()),
            description="Inventory Name",
            is_const=False,
        )
        # Vendor
        yield self.item(
            interface=interface,
            name="Vendor",
            value=o.model.vendor.name,
            description="Hardware vendor",
            is_const=True,
        )
        # Model
        model_choices = None
        for rg in self.RGROUPS:
            if o.model.name in rg:
                g = [ObjectModel.objects.get(name=x) for x in rg]
                model_choices = [[str(x.id), x.name] for x in g]
                break
        yield self.item(
            interface=interface,
            name="Model",
            value=o.model.name,
            description="Inventory Model",
            is_const=model_choices is None,
            choices=model_choices,
            item_id=str(o.model.id),
        )
        # ID
        yield self.item(
            interface=interface,
            name="ID",
            value=str(o.id),
            description="Internal ID",
            is_const=True,
        )
        if o.remote_system:
            # Remote system
            yield self.item(
                interface=interface,
                name="Remote System",
                value=o.remote_system.name,
                description="Remote System Name",
                is_const=True,
            )
            # Remote id
            yield self.item(
                interface=interface,
                name="RemoteID",
                value=o.remote_id,
                description="Remote System ID",
                is_const=True,
            )
        mo_id = o.get_data("management", "managed_object")
        if mo_id:
            mo = ManagedObject.get_by_id(int(mo_id))
            if mo:
                yield self.item(
                    interface=interface,
                    name="Managed Object",
                    value=f"{mo.name} [{mo.profile.name}]",
                    description="Managed Object",
                    is_const=True,
                    item_id=mo_id,
                )

    def iter_summary(self, o: Object) -> Iterable[Dict[str, Any]]:
        """
        Summary information
        """

        def get_summary(d: Dict[ObjectId, float]) -> float:
            r = 0.0
            for obj_id in nested_ids:
                om = obj_model.get(obj_id)
                if not om:
                    continue
                v = d.get(om)
                if v is not None:
                    r += v
            return r

        interface = "Summary"
        # All downwards objects
        nested_ids = o.get_nested_ids()
        # Object to model mapping
        obj_model = {
            doc["_id"]: doc["model"]
            for doc in Object._get_collection().find(
                {"_id": {"$in": nested_ids}}, {"_id": 1, "model": 1}
            )
        }
        # Get model data
        model_weight: Dict[ObjectId, float] = {}
        model_power: Dict[ObjectId, float] = {}
        for doc in ObjectModel._get_collection().find(
            {"_id": {"$in": list(obj_model.values())}}, {"_id": 1, "data": 1}
        ):
            md = doc.get("data")
            if not md:
                continue
            m_id = doc["_id"]
            for item in md:
                iface = item.get("interface")
                attr = item.get("attr")
                v = item.get("value")
                if not iface or not attr or not v:
                    continue
                if iface == "weight" and attr == "weight":
                    model_weight[m_id] = v
                elif iface == "power" and attr == "power":
                    model_power[m_id] = v
        # Summarize
        total_weight = get_summary(model_weight)
        total_power = get_summary(model_power)
        # Weigth
        if total_weight:
            yield self.item(
                interface=interface,
                name="Total Weight",
                value=f"{total_weight:.3f}",
                description="Total weight of all objects (kg)",
                is_const=True,
            )
        if total_power:
            yield self.item(
                interface=interface,
                name="Nominal Power",
                value=f"{total_power:.3f}",
                description="Calculated power consumption (W)",
                is_const=True,
            )
        if o.is_rack:
            f_usage = 0
            r_usage = 0
            for child in o.iter_children():
                if not child.is_rackmount:
                    continue
                units = child.get_data("rackmount", "units")
                if not units:
                    continue
                units = math.ceil(units)
                side = child.get_data("rackmount", "side")
                if not side:
                    continue
                if side == "f":
                    f_usage += units
                elif side == "r":
                    r_usage += units
            usage = max(f_usage, r_usage)
            yield self.item(
                interface=interface,
                name="Units Used",
                value=str(usage),
                description="Used rack units",
                is_const=True,
            )

    def iter_effective_data(self, o: Object) -> Iterable[Dict[str, Any]]:
        # Group by model interfaces
        mi_values: Dict[str, Dict[str, List[Tuple[Optional[str], str]]]] = {}
        for item in o.get_effective_data():
            if item.interface not in mi_values:
                mi_values[item.interface] = defaultdict(list)
            mi_values[item.interface][item.attr] += [(item.value, item.scope)]
        # Yield items
        for i in mi_values:
            mi = ModelInterface.get_by_name(i)
            if not mi:
                continue
            for a in mi.attrs:
                for value, scope in mi_values[i].get(a.name, [(None, "")]):
                    if value is None and a.is_const:
                        continue
                    yield self.item(
                        interface=i,
                        name=a.name,
                        scope=scope,
                        value=value,
                        type=a.type,
                        description=a.description,
                        required=a.required,
                        is_const=a.is_const,
                    )

    def api_save_data(self, request, id, interface=None, key=None, value=None):
        o = self.app.get_object_or_404(Object, id=id)
        if interface == "Common":
            # Fake interface
            if key == "Name":
                o.name = value.split("|")[-1].strip()
            elif key == "Model":
                m = self.app.get_object_or_404(ObjectModel, id=value)
                o.model = m
                o.log(message="Changing model to %s" % m.name, user=request.user, system="WEB")
                o.save()
        else:
            if value is None or value == "":
                o.reset_data(interface, key)
            else:
                o.set_data(interface, key, value)
        o.save()
