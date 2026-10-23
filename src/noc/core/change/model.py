# ----------------------------------------------------------------------
# @change Models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Literal
from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class ChangeField:
    field: str  # FieldName
    new: Any | None  # New Value
    new_label: str | None = None
    old: Any | None = None  # Old Value
    old_label: str | None = None


@dataclass(frozen=True)
class ChangeItem:
    op: Literal["create", "update", "delete"] = field(compare=False)
    model_id: str
    item_id: str
    changed_fields: list[ChangeField] | None = field(default=None, compare=False)
    changed_caps: list[str] | None = field(default=None, compare=False)
    domains: list[tuple[str, str]] | None = None  # model, id, op (in/out)
    affected_rules: list[str] | None = field(default=None, compare=False)
    # datastreams: Optional[List[Tuple[str, str]]] = None
    # groups
    # labels
    # Matcher
    ts: float | None = field(default=None, compare=False)
    user: str | None = field(default=None, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChangeItem":
        return ChangeItem(
            op=data["op"],
            model_id=data["model_id"],
            item_id=data["item_id"],
            changed_fields=[ChangeField(**cf) for cf in data.get("changed_fields") or []],
            changed_caps=data.get("changed_caps"),
            domains=data.get("domains"),
            affected_rules=data.get("affected_rules"),
            user=data.get("user"),
            ts=float(data["ts"]) if data.get("ts") else None,
        )

    @staticmethod
    def merge_fields(
        f1: list[ChangeField] | None, f2: list[ChangeField] | None
    ) -> list[ChangeField] | None:
        processed = set()
        r = []
        for x in f1 or []:
            r.append(x)
            processed.add(x.field)
        for x in f2 or []:
            if x.field not in processed:
                r.append(x)
        return r

    def change(self, op: str, changed_fields: list[ChangeField], timestamp: float | None = None):
        """
        Args:
            op:
            changed_fields:
            timestamp:
        """
        # Series of change
        if op == "delete":
            # Delete overrides any operation
            return replace(self, **{"op": op, "ts": timestamp, "changed_fields": None})
        if op == "create":
            raise RuntimeError("create must be first update")
        # Update
        if self.op == "create":
            # Create + Update -> Create with merged fields
            return replace(
                self, **{"changed_fields": self.merge_fields(self.changed_fields, changed_fields)}
            )
        if self.op == "update":
            # Update + Update -> Update with merged fields
            return replace(
                self, **{"changed_fields": self.merge_fields(self.changed_fields, changed_fields)}
            )
        if self.op == "delete":
            raise RuntimeError("Cannot update after delete")

    @property
    def instance(self):
        from noc.models import get_object

        return get_object(self.model_id, self.item_id)

    @property
    def key(self) -> int:
        """Calculate sharding key"""
        return hash(self.item_id)

    def is_change_field(self, name: str) -> bool:
        """Check field is changed"""
        return any(f.field == name for f in self.changed_fields)

    def get_field(self, name: str) -> ChangeField | None:
        """Getting changed fields"""
        for f in self.changed_fields:
            if f.field == name:
                return f
        return None
