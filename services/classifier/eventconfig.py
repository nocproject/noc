# ---------------------------------------------------------------------
# EventConfig for classification
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Dict, Callable, List, Optional, Any

# NOC modules
from noc.core.models.valuetype import ValueType
from noc.sa.interfaces.base import InterfaceTypeError
from noc.models import get_model
from .exception import EventProcessingFailed


@dataclass(frozen=True, slots=True)
class VarItem:
    name: str
    type: ValueType
    required: bool = False
    resource_model: Optional[str] = None


@dataclass(frozen=True, slots=True)
class FilterConfig:
    window: int
    vars: Optional[List[str]] = None


@dataclass(slots=True)
class EventConfig:
    name: str
    bi_id: int
    event_class: str
    event_class_id: str
    # categories: List[str]
    vars: List[VarItem]
    managed_object_required: bool = True
    filters: Optional[Dict[str, FilterConfig]] = None
    resources: Optional[Dict[str, Callable]] = None
    # EventActions
    # TargetActions
    # Resources
    actions: Optional[List[Callable]] = None

    @property
    def label(self):
        return self.event_class

    @property
    def id(self):
        return self.event_class_id

    @classmethod
    def resolve_resource(cls, v: VarItem, vv: Dict[str, Any], managed_object: Any):
        """"""
        m = get_model(v.resource_model)
        x = m.get_component(managed_object=managed_object, **vv)
        if x:
            vv[v.name] = x.name
            # self.logger.info(
            #     "[%s|%s] Interface not found:%s",
            #     # event.id,
            #     managed_object.name,
            #     managed_object.address,
            #     x,
            # )
        return x

    def eval_vars(self, r_vars: Dict[str, Any], managed_object: Any):
        """Evaluate rule variables"""
        r = {}
        # Resolve resource
        # resource -> var
        resources = {}
        # Resolve e_vars
        for ecv in self.vars:
            # Check variable is present
            if ecv.resource_model:
                resources[ecv.resource_model] = self.resolve_resource(
                    ecv,
                    r_vars,
                    managed_object,
                )
            if ecv.name not in r_vars:
                if ecv.required:
                    raise Exception("Required variable '%s' is not found" % ecv.name)
                continue
            # Decode variable
            try:
                v = ecv.type.clean_value(r_vars[ecv.name])
            except InterfaceTypeError:
                raise EventProcessingFailed(
                    "Cannot decode variable '%s'. Invalid %s: %s" % (ecv.name, ecv.type, repr(v))
                )
            r[ecv.name] = v
        return r, resources

    @classmethod
    def from_config(cls, data) -> "EventConfig":
        ec = EventConfig(
            name=data["name"],
            bi_id=data["bi_id"],
            event_class=data["event_class"]["name"],
            event_class_id=data["event_class"]["id"],
            managed_object_required=data["managed_object_required"],
            vars=[],
            filters={},
        )
        for ff in data["filters"]:
            ec.filters[ff["name"]] = FilterConfig(
                window=ff["window"],
                vars=[vv["name"] for vv in data["vars"] if vv["match_suppress"]],
            )
        for vv in data["vars"]:
            ec.vars += [
                VarItem(
                    name=vv["name"],
                    type=ValueType(vv["type"]),
                    required=vv["required"],
                    resource_model="inv.Interface" if vv["type"] == "interface_name" else None,
                ),
            ]
        # for rr in data["resources"]:
        #     ec.resolvers[rr["resource"]] = lambda x: True
        return ec
