# ----------------------------------------------------------------------
# @change Models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Any, Literal, List
from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class ChangeField(object):
    field: str  # FieldName
    new: Any  # New Value
    old: Optional[Any] = None  # Old Value
    # user: Optional[Any] = None  # Changed User


@dataclass(frozen=True)
class ChangeItem(object):
    op: Literal["create", "update", "delete"] = field(compare=False)
    model_id: str
    item_id: str
    changed_fields: Optional[List[ChangeField]] = field(default=None, compare=False)
    ts: Optional[float] = field(default=None, compare=False)
    user: Optional[str] = field(default=None, compare=False)

    @staticmethod
    def merge_fields(
        f1: Optional[List[ChangeField]], f2: Optional[List[ChangeField]]
    ) -> Optional[List[ChangeField]]:
        processed = set()
        r = []
        for x in f1 or []:
            r.append(x)
            processed.add(x.field)
        for x in f2 or []:
            if x.field not in processed:
                r.append(x)
        return r

    def change(self, op: str, changed_fields: List[ChangeField], timestamp: Optional[float] = None):
        """

        :param op:
        :param changed_fields:
        :param timestamp:
        :return:
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
        elif self.op == "update":
            # Update + Update -> Update with merged fields
            return replace(
                self, **{"changed_fields": self.merge_fields(self.changed_fields, changed_fields)}
            )
        elif self.op == "delete":
            raise RuntimeError("Cannot update after delete")

    @property
    def instance(self):
        from noc.models import get_object

        return get_object(self.model_id, self.item_id)
