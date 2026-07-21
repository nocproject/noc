# ----------------------------------------------------------------------
# Metrics source
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any, Literal

MetricKey = tuple[str, tuple[tuple[str, Any], ...], tuple[str, ...]]


@dataclass(frozen=True)
class SourceInfo:
    """
    Source Info for applied metric Card
    """

    __slots__ = (
        "bi_id",
        "composed_metrics",
        "fm_pool",
        "labels",
        "meta",
        "metric_labels",
        "rules",
        "sensor",
        "service",
        "sla_probe",
    )
    bi_id: int
    fm_pool: str
    sla_probe: str | None
    sensor: str | None
    service: str | None
    labels: list[str] | None
    metric_labels: list[str] | None
    composed_metrics: list[str] | None
    rules: list[str] | None
    meta: dict[str, Any]


@dataclass(frozen=True)
class ItemConfig:
    """
    Metric Source Item Config
    Match by key_labels
    """

    __slots__ = ("composed_metrics", "key_labels", "rules")
    key_labels: tuple[str, ...]  # noc::interface::*, noc::interface::Fa 0/24
    composed_metrics: tuple[str, ...]  # Metric Field for compose metrics
    rules: tuple[str, ...]

    def is_match(self, k: MetricKey) -> bool:
        return not set(self.key_labels) - set(k[2])


@dataclass(frozen=True)
class SourceConfig:
    """
    Configuration for Metric Source and Items.
    Contains configured metrics, labels and alarm node config
    Supported Source:
    * managed_object
    * agent
    * sla_probe
    * sensor
    """

    __slots__ = ("bi_id", "exposed_labels", "fm_pool", "items", "labels", "meta", "rules", "type")
    type: Literal["managed_object", "sla_probe", "sensor", "agent"]
    bi_id: int
    fm_pool: str
    labels: tuple[str, ...] | None
    exposed_labels: tuple[str, ...] | None
    items: tuple[ItemConfig, ...]
    rules: list[str]
    meta: dict[str, Any]

    def is_differ(self, sc: "SourceConfig"):
        """
        Compare Source Config
        * condition - Diff labels
        * items - Diff items
        * metrics (additional Compose Metrics)
        :return:
        """
        r = []
        if set(self.labels).difference(sc.labels):
            r += ["condition"]
        if set(self.exposed_labels or []).difference(sc.exposed_labels or []):
            r += ["condition"]
        return r


@dataclass
class ManagedObjectInfo:
    __slots__ = ("bi_id", "fm_pool", "id", "labels", "metric_labels")
    id: int
    bi_id: int
    fm_pool: str
    labels: list[str] | None
    metric_labels: list[str] | None
