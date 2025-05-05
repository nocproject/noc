# ---------------------------------------------------------------------
# EventConfig for classification
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Dict, Callable, List, Optional

# NOC modules
from noc.core.models.valuetype import ValueType


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
                    resource_model=vv.get("resource_model"),
                ),
            ]
        # for rr in data["resources"]:
        #     ec.resolvers[rr["resource"]] = lambda x: True
        return ec
