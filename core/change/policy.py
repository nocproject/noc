# ----------------------------------------------------------------------
# Change tracking policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import contextlib
import time
from contextvars import ContextVar
from collections import defaultdict
from typing import Optional, Tuple, List, Dict, Literal, Set
from abc import ABCMeta, abstractmethod


# NOC modules
from noc.core.defer import defer
from noc.core.hash import hash_int
from .model import ChangeItem
from noc.models import get_model

CHANGE_HANDLER = "noc.core.change.change.on_change"
DS_APPLY_HANDLER = "noc.core.change.change.apply_datastream"
BI_APPLY_HANDLER = "noc.core.change.change.apply_ch_dictionary"
# inv.ObjectModel and sensors, inv.Object and data
SYNC_SENSOR_HANDLER = "noc.core.change.change.apply_sync_sensors"
AUDIT_CHANGE = "noc.core.change.change.audit_change"

cv_policy: ContextVar[Optional["BaseChangeTrackerPolicy"]] = ContextVar("cv_policy", default=None)
cv_policy_stack: ContextVar[Optional[List["BaseChangeTrackerPolicy"]]] = ContextVar(
    "cv_policy_stack", default=None
)

CHANGE_HANDLERS: Dict[str, Set[str]] = defaultdict(set)
CHUNK_SIZE = 1000


class ChangeTracker(object):
    """
    Thread-local change tracker.
    """

    @staticmethod
    def load_receivers() -> None:
        """
        Return changes receiver
        :return:
        """
        from noc.core.bi.dictionaries.loader import loader

        for dcls_name in loader:
            bi_dict_model = loader[dcls_name]
            if not bi_dict_model:
                continue
            mongo_model = get_model(bi_dict_model._meta.source_model)
            if hasattr(mongo_model, "flag_audit"):
                CHANGE_HANDLERS[bi_dict_model._meta.source_model].add(AUDIT_CHANGE)
            CHANGE_HANDLERS[bi_dict_model._meta.source_model].add(BI_APPLY_HANDLER)
        CHANGE_HANDLERS["inv.ObjectModel"].add(SYNC_SENSOR_HANDLER)
        CHANGE_HANDLERS["inv.Object"].add(SYNC_SENSOR_HANDLER)

    @staticmethod
    def get_policy() -> "BaseChangeTrackerPolicy":
        policy = cv_policy.get()
        if not policy:
            policy = SimpleChangeTrackerPolicy()
            cv_policy.set(policy)
        return policy

    def register(
        self,
        op: Literal["create", "update", "delete"],
        model: str,
        id: str,
        fields: Optional[List] = None,
        datastreams: Optional[List[Tuple[str, str]]] = None,
        audit: bool = False,
    ) -> None:
        """
        Register datastream change
        :param op: Operation, either create, update or delete
        :param model: Model id
        :param id: Item id
        :param fields: List of changed fields
        :param datastreams: List of changed datastream
        :param audit: Send Changes to Audit Log
        :return:
        """
        from noc.core.middleware.tls import get_user

        if not CHANGE_HANDLERS:
            self.load_receivers()
        self.get_policy().register(
            item=ChangeItem(
                op=op,
                model_id=model,
                item_id=id,
                ts=time.time(),
                user=str(get_user()),
                changed_fields=fields,
            )
        )
        if datastreams:
            self.get_policy().register_ds(items=datastreams)  # Handler -> Change

    @staticmethod
    def push_policy(policy: "BaseChangeTrackerPolicy") -> None:
        """
        Push new effective policy for the current thread,
        store current one in the stack
        :param policy:
        :return:
        """
        # Store previous policy
        prev_policy = cv_policy.get()
        if prev_policy:
            # Something to store
            stack = cv_policy_stack.get() or []
            stack.append(prev_policy)
            cv_policy_stack.set(stack)
        # Store current policy
        cv_policy.set(policy)

    @staticmethod
    def pop_policy() -> Optional["BaseChangeTrackerPolicy"]:
        """
        Pop current effective policy from stack and restore previous one
        :return: Current effective policy
        """
        # Get current policy
        policy = cv_policy.get()
        stack = cv_policy_stack.get()
        if stack:
            # Install previous policy
            prev_policy = stack.pop(-1)
            cv_policy.set(prev_policy)
            if not stack:
                cv_policy_stack.set(None)
        return policy

    @contextlib.contextmanager
    def bulk_changes(self):
        """
        Apply all changes at once
        :return:
        """
        # Store current effective policy
        prev_policy = cv_policy.get()
        # Install bulk change policy as
        policy = BulkChangeTrackerPolicy()
        cv_policy.set(policy)
        yield
        policy.commit()
        cv_policy.set(prev_policy)


change_tracker = ChangeTracker()


class BaseChangeTrackerPolicy(object, metaclass=ABCMeta):
    """
    Base class for change tracker policies
    """

    def __init__(self):
        ...

    @abstractmethod
    def register(self, item: ChangeItem) -> None:
        ...

    @abstractmethod
    def register_ds(self, items: List[Tuple[str, str]]) -> None:
        ...


class DropChangeTrackerPolicy(BaseChangeTrackerPolicy):
    """
    Drop all changes
    """

    def register(self, item: ChangeItem) -> None:
        pass

    def register_ds(self, items: List[Tuple[str, str]]) -> None:
        pass


class SimpleChangeTrackerPolicy(BaseChangeTrackerPolicy):
    """
    Simple policy, applies every registered change
    """

    def register(self, item: ChangeItem) -> None:
        for handler in CHANGE_HANDLERS.get(item.model_id, []):
            defer(handler, key=hash(item), changes=[item])

    def register_ds(self, items: Optional[List[Tuple[str, str]]]):
        defers: Dict[int, Dict[str, Set[str]]] = {}
        for ds_name, item_id in items:
            key = hash_int(item_id)
            if key not in defers:
                defers[key] = defaultdict(set)
            defers[key][ds_name].add(str(item_id))
        for key, ds_changes in defers.items():
            for ds_name, changes in ds_changes.items():
                changes = list(changes)
                while changes:
                    chunk, changes = changes[:CHUNK_SIZE], changes[CHUNK_SIZE:]
                    defer(DS_APPLY_HANDLER, key=key, ds_changes={ds_name: list(chunk)})


class BulkChangeTrackerPolicy(BaseChangeTrackerPolicy):
    def __init__(self):
        super().__init__()
        self.changes: Dict[str, Dict[int, ChangeItem]] = defaultdict(dict)
        self.ds_changes: Dict[str, Set[str]] = defaultdict(set)

    def register(self, item: ChangeItem) -> None:
        key = hash(item)
        for handler in CHANGE_HANDLERS.get(item.model_id, []):
            changes = self.changes[handler]
            prev = changes.get(key)
            if prev is None:
                # First change
                changes[key] = item
                return
            prev = (
                prev.change(item.op, changed_fields=item.changed_fields, timestamp=item.ts) or prev
            )
            changes[key] = prev

    def register_ds(self, items: List[Tuple[str, str]]) -> None:
        # Changed datastreams
        for ds_name, item_id in items or []:
            self.ds_changes[ds_name].add(str(item_id))

    def commit(self) -> None:
        # Split to buckets
        # changes = defaultdict(list)
        # for (model_id, item_id), (op, fields, ts) in self.changes.items():
        #     part = 0
        #     changes[part].append((op, model_id, item_id, fields, ts))
        for handler, changes in self.changes.items():
            # for key, items in changes.items():
            key = 0
            defer(handler, key=key, changes=list(changes.values()))
        for k, v in self.ds_changes.items():
            for item_id in v:
                defer(DS_APPLY_HANDLER, key=hash_int(item_id), ds_changes={k: [item_id]})
        # if self.ds_changes:
        #     defer(
        #         DS_APPLY_HANDLER, key=0, ds_changes={k: list(v) for k, v in self.ds_changes.items()}
        #     )
