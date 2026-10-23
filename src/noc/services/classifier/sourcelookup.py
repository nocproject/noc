# ---------------------------------------------------------------------
# Source lookup table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from collections.abc import Iterable

# NOC modules
from noc.core.fm.event import Target
from noc.sa.models.managedobject import ManagedObject


@dataclass(eq=True, frozen=True)
class SourceConfig:
    id: str
    name: str
    bi_id: int
    address: str
    fm_pool: str
    sa_profile: str | None = None
    effective_labels: tuple[str, ...] = None
    watchers: tuple[str, ...] | None = None
    services: tuple[int, ...] | None = None
    mapping_refs: tuple[str, ...] | None = None

    @classmethod
    def from_data(cls, data) -> "SourceConfig":
        return SourceConfig(
            id=str(data["id"]),
            name=data["name"],
            bi_id=int(data["bi_id"]),
            address=data["addresses"][0]["address"] if data["addresses"] else None,
            fm_pool=data["fm_pool"],
            sa_profile=data.get("sa_profile"),
            effective_labels=tuple(data.get("effective_labels") or []),
            watchers=tuple(data.get("watchers") or []),
            services=tuple(int(svc["bi_id"]) for svc in data.get("services") or []),
            mapping_refs=tuple(data.get("mapping_refs") or []),
        )

    def is_diff(self, cfg: "SourceConfig") -> bool:
        """Check diff"""
        return cfg != self

    def get_mappings(self) -> Iterable[str]:
        """Getting mappings for source"""
        if not self.mapping_refs:
            return []
        return self.mapping_refs


class SourceLookup:
    def __init__(self) -> None:
        self.source_configs: dict[str, SourceConfig] = {}  # id -> SourceConfig
        self.source_map: dict[str, str] = {}

    def resolve_object(
        self, target: Target, remote_system: str | None = None
    ) -> ManagedObject | None:
        """
        Resolve Managed Object by target

        Args:
            target: Event Target
            remote_system: Remote System name
        """
        mo = None
        if target.id and not target.is_agent:
            mo = ManagedObject.get_by_id(int(target.id))
        if mo or not remote_system:
            return mo
        if target.remote_id and f"rs:{remote_system}:{target.remote_id}" in self.source_map:
            mo = self.source_map[f"rs:{remote_system}:{target.remote_id}"]
        if not mo and f"name:{target.name.lower()}" in self.source_map:
            mo = self.source_map[f"name:{target.name.lower()}"]
        if not mo and f"addr:{target.pool}:{target.address}" in self.source_map:
            mo = self.source_map[f"addr:{target.pool}:{target.address}"]
        if mo:
            return ManagedObject.get_by_id(int(mo))

    def resolve_target(
        self, target: Target, remote_system: str | None = None
    ) -> SourceConfig | None:
        """
        Resolve Managed Object by target

        Args:
            target: Event Target
            remote_system: Remote System name
        """
        sid = None
        if target.id and not target.is_agent and target.id in self.source_configs:
            return self.source_configs[target.id]
        if target.remote_id and f"rs:{remote_system}:{target.remote_id}" in self.source_map:
            sid = self.source_map[f"rs:{remote_system}:{target.remote_id}"]
        if not sid and f"name:{target.name.lower()}" in self.source_map:
            sid = self.source_map[f"name:{target.name.lower()}"]
        if not sid and f"addr:{target.pool}:{target.address}" in self.source_map:
            sid = self.source_map[f"addr:{target.pool}:{target.address}"]
        if sid in self.source_configs:
            return self.source_configs[sid]

    def delete_source(self, sid: str) -> bool:
        """Remove Source"""
        if sid not in self.source_configs:
            return False
        source = self.source_configs.pop(sid)
        for m in source.mapping_refs:
            if m in self.source_map:
                del self.source_map[m]
        return True

    def update_mappings(self, sid, new: Iterable[str], old: Iterable[str] | None = None):
        """"""
        # Delete Old Mappings
        for m in set(old or []) - set(new):
            if m in self.source_map:
                del self.source_map[m]
        # Add new Mappings
        for m in set(new) - set(old or []):
            self.source_map[m] = sid

    def update_source(self, data) -> bool:
        """"""
        try:
            s = SourceConfig.from_data(data)
        except Exception as e:
            print(f"{data['id']}Error when processed source: {e}")
            return False
        if s.id not in self.source_configs:
            self.update_mappings(s.id, s.get_mappings())
        else:
            if not self.source_configs[s.id].is_diff(s):
                return False
            self.update_mappings(s.id, s.get_mappings(), self.source_configs[s.id].get_mappings())
        self.source_configs[s.id] = s
        return True
