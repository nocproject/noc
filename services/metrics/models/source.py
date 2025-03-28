# ----------------------------------------------------------------------
# Metrics source
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any, Tuple, List, Optional, Literal, Dict

MetricKey = Tuple[str, Tuple[Tuple[str, Any], ...], Tuple[str, ...]]


@dataclass(frozen=True)
class SourceInfo(object):
    """
    Source Info for applied metric Card
    """

    __slots__ = (
        "bi_id",
        "sensor",
        "sla_probe",
        "service",
        "fm_pool",
        "labels",
        "metric_labels",
        "composed_metrics",
        "rules",
        "meta",
    )
    bi_id: int
    fm_pool: str
    sla_probe: Optional[str]
    sensor: Optional[str]
    service: Optional[str]
    labels: Optional[List[str]]
    metric_labels: Optional[List[str]]
    composed_metrics: Optional[List[str]]
    rules: Optional[List[str]]
    meta: Dict[str, Any]


@dataclass(frozen=True)
class ItemConfig(object):
    """
    Metric Source Item Config
    Match by key_labels
    """

    __slots__ = ("key_labels", "composed_metrics", "rules")
    key_labels: Tuple[str, ...]  # noc::interface::*, noc::interface::Fa 0/24
    composed_metrics: Tuple[str, ...]  # Metric Field for compose metrics
    rules: Tuple[str, ...]

    def is_match(self, k: MetricKey) -> bool:
        return not set(self.key_labels) - set(k[2])


@dataclass(frozen=True)
class SourceConfig(object):
    """
    Configuration for Metric Source and Items.
    Contains configured metrics, labels and alarm node config
    Supported Source:
    * managed_object
    * agent
    * sla_probe
    * sensor
    """

    __slots__ = ("type", "bi_id", "fm_pool", "labels", "items", "rules", "meta")
    type: Literal["managed_object", "sla_probe", "sensor", "agent"]
    bi_id: int
    fm_pool: str
    labels: Optional[Tuple[str, ...]]
    items: Tuple[ItemConfig, ...]
    rules: List[str]
    meta: Dict[str, Any]

    def is_differ(self, sc: "SourceConfig"):
        """
        Compare Source Config
        * condition - Diff labels
        * items - Diff items
        * metrics (additional Compose Metrics)
        :param sc:
        :return:
        """
        r = []
        if set(self.labels).difference(sc.labels):
            r += ["condition"]
        return r


@dataclass
class ManagedObjectInfo(object):
    __slots__ = ("id", "bi_id", "fm_pool", "labels", "metric_labels")
    id: int
    bi_id: int
    fm_pool: str
    labels: Optional[List[str]]
    metric_labels: Optional[List[str]]
