# ----------------------------------------------------------------------
# Metrics source
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from dataclasses import dataclass
from typing import Any, Tuple, Optional, Dict, FrozenSet, Union, ClassVar

MetricKey = Tuple[str, Tuple[Tuple[str, Any], ...], Tuple[str, ...]]


@dataclass(frozen=True, slots=True)
class ComponentTarget:
    key_labels: Tuple[str, ...]  # noc::interface::*, noc::interface::Fa 0/24
    rules: Tuple[str, ...]
    composed_metrics: Tuple[str, ...]  # Metric Field for compose metrics
    exposed_labels: Optional[Tuple[str, ...]]

    @classmethod
    def from_data(cls, data):
        """Create Instance from data"""
        return ComponentTarget(
            key_labels=tuple(sys.intern(ll) for ll in data["key"]),
            rules=data.get("rules"),
            composed_metrics=tuple(sys.intern(m) for m in data.get("composed_metrics") or []),
            exposed_labels=None,
        )


@dataclass(frozen=True, slots=True)
class MetricTarget:
    type: ClassVar[str]

    id: str
    bi_id: int
    managed_object: Optional[int]
    fm_pool: Optional[str]
    rules: Optional[Tuple[str, ...]]
    exposed_labels: Optional[Tuple[str, ...]]
    composed_metrics: Optional[Tuple[str, ...]]
    # not_save_metrics

    @classmethod
    def from_config(
        cls, data: Dict[str, Any], r_type: str
    ) -> Optional[Union["ManagedObjectTarget", "SensorTarget", "SLAProbeTarget"]]:
        """Return classes"""
        if "$deleted" in data or r_type == "remote_system":
            return None
        fm_pool = data.get("fm_pool")
        if fm_pool:
            fm_pool = sys.intern(fm_pool)
        params = {
            "id": data.get("id", data["bi_id"]),
            "bi_id": data["bi_id"],
            "managed_object": data.get("managed_object"),
            "fm_pool": fm_pool,
            "rules": data.get("rules"),
            "exposed_labels": tuple(sys.intern(ll) for ll in data.get("exposed_labels", [])),
            "composed_metrics": tuple(sys.intern(ll) for ll in data.get("composed_metrics", [])),
        }
        match r_type:
            case "managed_object":
                params |= {
                    "opaque_data": data.get("opaque_data"),
                    "managed_object": data["bi_id"],
                    "components": tuple(
                        ComponentTarget.from_data(d) for d in data.get("items", [])
                    ),
                    "sensors": frozenset(d["bi_id"] for d in data.get("sensors", [])),
                }
                return ManagedObjectTarget(**params)
            case "sla":
                return SLAProbeTarget(**params)
            case "sensor":
                params["units"] = data["units"]
                return SensorTarget(**params)
            case _:
                return None


@dataclass(frozen=True, slots=True)
class ManagedObjectTarget(MetricTarget):
    type = "managed_object"

    opaque_data: Optional[Dict[str, Any]]
    components: Optional[Tuple[ComponentTarget, ...]]
    # For changes
    # Exclude compare
    sensors: Optional[FrozenSet[int]]

    @property
    def meta(self):
        return self.opaque_data


@dataclass(frozen=True, slots=True)
class SensorTarget(MetricTarget):
    type = "sensor"

    units: str


@dataclass(frozen=True, slots=True)
class SLAProbeTarget(MetricTarget):
    type = "sla_probe"

    opaque: Optional[Dict[str, Any]]

    @property
    def meta(self):
        return self.opaque
