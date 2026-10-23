# ----------------------------------------------------------------------
# cfgmetricstarget datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Literal, Any

# Third-party modules
from pydantic import BaseModel

# NOC Modules
from .utils import ManagedObjectOpaque


class SensorItem(BaseModel):
    bi_id: int
    name: str
    units: str
    exposed_labels: list[str] | None = None
    rules: list[str] | None = None
    profile: str | None = None
    protocol: str = "other"
    mx_alias: str | None = None
    hints: list[str] | None = None


class MetricItem(BaseModel):
    key: Any
    # key_Hash ?
    composed_metrics: list[str] | None = None
    exposed_labels: list[str] | None = None
    rules: list[str] | None = None


class RemoteChannelItem(BaseModel):
    policy: Literal["D", "E", "S"]
    batch_signal: Literal["A", "D", "B"] = "A"
    batch_size: int = 5_000
    batch_delay_s: int = 10
    enable_event: bool = False
    enable_metrics: bool = False


class CfgMetricsTarget(BaseModel):
    id: str  # Record id     # Split Config/Part
    type: Literal["managed_object", "sensor", "sla", "agent", "remote_system"]
    name: str
    bi_id: int
    sharding_key: int
    # Service
    services: list[str] | None = None
    mapping_refs: list[str] | None = None
    # Collector received
    enable_fmevent: bool = False
    enable_metrics: bool = True
    profile: str | None = None
    api_key: str | None = None  # Auth Key
    nodata_policy: str = "D"
    nodata_ttl: int | None = None
    discovery_interval: int | None = None
    # Allowed address
    addresses: list[str] | None = None
    # mirroring - mirror to collection
    # FM
    fm_pool: str | None = None
    # metric_key
    # key -> Rule
    channel: RemoteChannelItem | None = None
    managed_object: int | None = None
    exposed_labels: list[str] | None = None
    rules: list[str] | None = None
    # Optional, if rule, composed metrics or config set
    composed_metrics: list[str] | None = None
    opaque_data: ManagedObjectOpaque | None = None  # Kafka message data
    items: list[MetricItem] | None = None
    sensors: list[SensorItem] | None = None
