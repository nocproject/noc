# ---------------------------------------------------------------------
# Source Config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Tuple, Optional, Iterable, List

# NOC Modules
from noc.config import config


@dataclass
class RemoteSystemConfig(object):
    id: str
    name: str
    bi_id: int
    api_key: Optional[str] = None
    code: Optional[str] = None
    is_banned: bool = False
    enable_event: bool = True
    enable_metrics: bool = True
    policy: str = "E"
    batch_signal: str = "A"
    batch_size: Optional[int] = 50000
    batch_delay_s: Optional[int] = 10

    @classmethod
    def from_data(cls, data) -> "RemoteSystemConfig":
        cfg = data.get("channel") or {}
        if not cfg:
            cfg |= {
                "batch_size": config.metricscollector.batch_size,
                "batch_delay_s": config.metricscollector.batch_delay_s,
            }
        cfg |= {
            "id": str(data["id"]),
            "name": data["name"],
            "bi_id": int(data["bi_id"]),
            "api_key": data.get("api_key"),
        }
        return RemoteSystemConfig(**cfg)


@dataclass(eq=True, frozen=True)
class SensorConfig(object):
    name: str
    bi_id: int
    units: str = "1"
    managed_object: Optional[int] = None
    hints: Optional[Tuple[str, ...]] = None

    @classmethod
    def from_data(cls, data, managed_object: Optional[int] = None) -> "SensorConfig":
        return SensorConfig(
            name=data["name"],
            bi_id=data["bi_id"],
            units=data["units"],
            managed_object=managed_object,
            hints=data.get("hints"),
        )

    @property
    def id(self):
        return str(self.bi_id)

    def get_mappings(self) -> List[str]:
        return self.hints or []


@dataclass(eq=True, frozen=True)
class SourceConfig(object):
    id: str
    name: str
    bi_id: int
    address: str
    fm_pool: str
    api_key: str
    managed_object: Optional[int] = None
    enable_metrics: bool = False
    enable_fmevent: bool = False
    no_data_check: bool = False
    mapping_refs: Optional[Tuple[str, ...]] = None
    sensors: Optional[Tuple[str, ...]] = None

    @classmethod
    def from_data(cls, data) -> "SourceConfig":
        mappings, keys, sensors = [], [], []
        for m in data.get("mapping_refs") or []:
            mappings.append(m)
        if data.get("api_key"):
            keys.append(data["api_key"])
        for s in data.get("sensors", []):
            sensors.append(str(s["bi_id"]))
        mo = None
        if data["type"] == "managed_object":
            mo = data["bi_id"]
        return SourceConfig(
            id=str(data["id"]),
            name=data["name"],
            bi_id=int(data["bi_id"]),
            address=data["addresses"][0] if data.get("addresses") else None,
            fm_pool=data.get("fm_pool"),
            api_key=data.get("api_key"),
            enable_metrics=bool(data.get("enable_metrics")),
            enable_fmevent=bool(data.get("enable_fmevent")),
            no_data_check=data.get("nodata_policy") == "C",
            managed_object=mo,
            mapping_refs=tuple(mappings),
            sensors=tuple(sensors),
        )

    def is_diff(self, cfg: "SourceConfig") -> bool:
        """Check diff"""
        return cfg != self

    def get_mappings(self) -> Iterable[str]:
        """Getting mappings for source"""
        if not self.mapping_refs:
            return []
        return self.mapping_refs
