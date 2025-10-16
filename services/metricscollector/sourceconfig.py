# ---------------------------------------------------------------------
# Source Config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Tuple, Optional, Iterable, FrozenSet


@dataclass(eq=True, frozen=True)
class RemoteCollectors:
    name: str
    api_key: str
    bi_id: Optional[int]
    enable_metrics: bool = False

    @classmethod
    def from_data(cls, data) -> "RemoteCollectors":
        """Build RemoteSystem from data"""
        return RemoteCollectors(
            name=data["name"],
            api_key=data["api_key"],
            bi_id=data.get("bi_id"),
            enable_metrics=bool(data.get("enable_metrics")),
        )


@dataclass(eq=True, frozen=True)
class SourceConfig(object):
    id: str
    name: str
    bi_id: int
    address: str
    fm_pool: str
    api_keys: FrozenSet[str]
    no_data_check: bool = False
    mapping_refs: Optional[Tuple[str, ...]] = None
    collectors: Optional[FrozenSet[RemoteCollectors]] = None

    @classmethod
    def from_data(cls, data) -> "SourceConfig":
        mappings, collectors, keys = [], [], []
        for rc in data.get("metric_collector") or []:
            rc = RemoteCollectors.from_data(rc)
            collectors.append(rc)
            if rc.api_key:
                keys.append(rc.api_key)
        for m in data.get("mapping_refs") or []:
            mappings.append(m)
        return SourceConfig(
            id=str(data["id"]),
            name=data["name"],
            bi_id=int(data["bi_id"]),
            address=data["addresses"][0]["address"] if data["addresses"] else None,
            fm_pool=data["fm_pool"],
            api_keys=frozenset(keys),
            mapping_refs=tuple(mappings),
            collectors=frozenset(collectors),
        )

    def is_diff(self, cfg: "SourceConfig") -> bool:
        """Check diff"""
        return cfg != self

    def get_mappings(self) -> Iterable[str]:
        """Getting mappings for source"""
        if not self.mapping_refs:
            return []
        return self.mapping_refs

    def get_remote_collector_by_key(self, key: str) -> Optional[RemoteCollectors]:
        """Getting Remote Collector by key"""
        if not self.collectors:
            return None
        for c in self.collectors:
            if c.api_key == key:
                return c
        return None

    def has_remote_system(self, name) -> bool:
        """Check source on RemoteSystem"""
        return any(rc.name == name for rc in self.collectors or [])
