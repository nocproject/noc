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
class SourceConfig(object):
    id: str
    name: str
    bi_id: int
    address: str
    fm_pool: str
    mapping_refs: Optional[Tuple[str, ...]] = None
    remote_systems: Optional[FrozenSet[str]] = None

    @classmethod
    def from_data(cls, data) -> "SourceConfig":
        mappings, rs_names = [], []
        for m in data.get("mapping_refs") or []:
            mappings.append(m)
            if m.startswith("rs"):
                rs_names.append(m.split(":")[1].lower())
        return SourceConfig(
            id=str(data["id"]),
            name=data["name"],
            bi_id=int(data["bi_id"]),
            address=data["addresses"][0]["address"] if data["addresses"] else None,
            fm_pool=data["fm_pool"],
            mapping_refs=tuple(mappings),
            remote_systems=frozenset(rs_names),
        )

    def is_diff(self, cfg: "SourceConfig") -> bool:
        """Check diff"""
        return cfg != self

    def get_mappings(self) -> Iterable[str]:
        """Getting mappings for source"""
        if not self.mapping_refs:
            return []
        return self.mapping_refs

    def has_remote_system(self, name) -> bool:
        """Check source on RemoteSystem"""
        return name in self.remote_systems
