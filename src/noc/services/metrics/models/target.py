# ----------------------------------------------------------------------
# Metrics source
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from dataclasses import dataclass
from typing import Any, Union, ClassVar

MetricKey = tuple[str, tuple[tuple[str, int], ...], tuple[str, ...]]


def convert_rules(rules: list[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    """"""
    r = []
    for rule_id, action_id in rules:
        r.append((sys.intern(str(rule_id)), sys.intern(str(action_id))))
    return tuple(r)


@dataclass(frozen=True, slots=True)
class ComponentTarget:
    key_labels: tuple[str, ...]  # noc::interface::*, noc::interface::Fa 0/24
    rules: tuple[tuple[str, str], ...] | None
    composed_metrics: tuple[str, ...]  # Metric Field for compose metrics
    exposed_labels: tuple[str, ...] | None

    @classmethod
    def from_data(cls, data):
        """Create Instance from data"""
        return ComponentTarget(
            key_labels=tuple(sys.intern(ll) for ll in data["key"]),
            rules=convert_rules(data.get("rules", [])),
            composed_metrics=tuple(sys.intern(m) for m in data.get("composed_metrics") or []),
            exposed_labels=None,
        )


@dataclass(frozen=True, slots=True)
class MetricTarget:
    type: ClassVar[str]

    id: str
    bi_id: int
    managed_object: int | None
    fm_pool: str | None
    rules: tuple[tuple[str, str], ...] | None
    exposed_labels: tuple[str, ...] | None
    composed_metrics: tuple[str, ...] | None
    # not_save_metrics

    @classmethod
    def from_config(
        cls, data: dict[str, Any], r_type: str
    ) -> Union["ManagedObjectTarget", "SLAProbeTarget"] | None:
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
            "rules": convert_rules(data.get("rules", [])),
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
            case _:
                return None


@dataclass(frozen=True, slots=True)
class ManagedObjectTarget(MetricTarget):
    type = "managed_object"

    opaque_data: dict[str, Any] | None
    components: tuple[ComponentTarget, ...] | None
    # For changes
    # Exclude compare
    sensors: frozenset[int] | None

    @property
    def meta(self):
        return self.opaque_data


@dataclass(frozen=True, slots=True)
class SLAProbeTarget(MetricTarget):
    type = "sla_probe"

    opaque: dict[str, Any] | None
    service: int | None = None

    @property
    def meta(self):
        return self.opaque


@dataclass(frozen=True, slots=True)
class SensorComponentTarget:
    id: str
    bi_id: int
    name: str | None
    units: str | None
    mx_alias: str | None
    target: MetricTarget | None
    managed_object: int | None
    agent: int | None
    rules: tuple[tuple[str, str], ...] | None
    exposed_labels: tuple[str, ...] | None

    @classmethod
    def from_config(cls, data, target: MetricTarget | None = None):
        """Create Instance from data"""
        return SensorComponentTarget(
            id=str(data["id"]),
            bi_id=int(data["bi_id"]),
            name=data.get("name"),
            managed_object=int(data["managed_object"]) if "managed_object" in data else None,
            agent=int(data["agent"]) if "agent" in data else None,
            rules=convert_rules(data.get("rules", [])),
            exposed_labels=None,
            units=data.get("units", "1"),
            mx_alias=data.get("mx_alias"),
            target=target,
        )

    @property
    def meta(self):
        if self.target:
            return self.target.meta
        return None

    @property
    def composed_metrics(self):
        return None
