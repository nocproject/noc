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
from .exception import EventProcessingFailed


@dataclass(frozen=True, slots=True)
class VarItem:
    name: str
    type: ValueType
    required: bool = False


@dataclass
class EventConfig:
    name: str
    bi_id: int
    event_class: str
    event_class_id: str
    # categories: List[str]
    vars: List[VarItem]
    managed_object_required: bool = True
    filters: Optional[Dict[str, int]] = None
    resolvers: Optional[Dict[str:Callable]] = None
    actions: Optional[List[Callable]] = None

    @property
    def label(self):
        return self.event_class

    @property
    def id(self):
        return self.event_class_id

    def eval_vars(self, r_vars: Dict[str, Any]):
        """Evaluate rule variables"""
        r = {}
        # Resolve e_vars
        for ecv in self.vars:
            # Check variable is present
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
        return r
