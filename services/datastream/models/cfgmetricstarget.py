# ----------------------------------------------------------------------
# cfgmetricstarget datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Literal, Any

# Third-party modules
from pydantic import BaseModel

# NOC Modules
from .utils import ManagedObjectOpaque


class SensorItem(BaseModel):
    bi_id: int
    name: str
    units: str
    exposed_labels: Optional[List[str]] = None
    rules: Optional[List[str]] = None
    profile: Optional[str] = None
    protocol: str = "other"
    hints: Optional[List[str]] = None


class MetricItem(BaseModel):
    key: Any
    # key_Hash ?
    composed_metrics: Optional[List[str]] = None
    exposed_labels: Optional[List[str]] = None
    rules: Optional[List[str]] = None


class CfgMetricsTarget(BaseModel):
    id: str  # Record id     # Split Config/Part
    type: Literal["managed_object", "sensor", "sla", "agent", "remote_system"]
    name: str
    bi_id: int
    sharding_key: int
    # Service
    mapping_refs: Optional[List[str]] = None
    # Collector received
    enable_fmevent: bool = False
    enable_metrics: bool = True
    profile: Optional[str] = None
    api_key: Optional[str] = None  # Auth Key
    nodata_policy: str = "D"
    nodata_ttl: Optional[int] = None
    discovery_interval: Optional[int] = None
    # Allowed address
    addresses: Optional[List[str]] = None
    # mirroring - mirror to collection
    # FM
    fm_pool: Optional[str] = None
    # metric_key
    # key -> Rule
    managed_object: Optional[int] = None
    exposed_labels: Optional[List[str]] = None
    rules: Optional[List[str]] = None
    # Optional, if rule, composed metrics or config set
    composed_metrics: Optional[List[str]] = None
    opaque_data: Optional[ManagedObjectOpaque] = None  # Kafka message data
    items: Optional[List[MetricItem]] = None
    sensors: Optional[List[SensorItem]] = None
