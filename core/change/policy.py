# ----------------------------------------------------------------------
# Change tracking policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import contextlib
from contextvars import ContextVar
import time
from collections import defaultdict
from typing import Optional, Tuple, List, Dict, Literal
from abc import ABCMeta, abstractmethod


# NOC modules
from noc.core.defer import defer
from noc.core.hash import hash_int
from .model import ChangeField

CHANGE_HANDLER = "noc.core.change.change.on_change"


cv_policy: ContextVar[Optional["BaseChangeTrackerPolicy"]] = ContextVar("cv_policy", default=None)
cv_policy_stack: ContextVar[Optional[List["BaseChangeTrackerPolicy"]]] = ContextVar(
    "cv_policy_stack", default=None
)


class ChangeTracker(object):
    """
    Thread-local change tracker.
    """

    @staticmethod
    def get_policy() -> "BaseChangeTrackerPolicy":
        policy = cv_policy.get()
        if not policy:
            policy = SimpleChangeTrackerPolicy()
            cv_policy.set(policy)
        return policy

    def register(self, op: str, model: str, id: str, fields: Optional[List] = None) -> None:
        """
        Register datastream change
        :param op: Operation, either create, update or delete
        :param model: Model id
        :param id: Item id
        :param fields: List of changed fields
        :return:
        """
        self.get_policy().register(op, model, id, fields)

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
    def register(self, op: str, model: str, id: str, fields: Optional[List] = None) -> None:
        ...


class DropChangeTrackerPolicy(BaseChangeTrackerPolicy):
    """
    Drop all changes
    """

    def register(self, op: str, model: str, id: str, fields: Optional[List] = None) -> None:
        pass


class SimpleChangeTrackerPolicy(BaseChangeTrackerPolicy):
    """
    Simple policy, applies every registered change
    """

    def register(
        self,
        op: Literal["create", "delete", "update"],
        model: str,
        id: str,
        fields: Optional[List[ChangeField]] = None,
    ) -> None:
        key = hash_int(id)
        t0 = time.time()
        defer(CHANGE_HANDLER, key=key, changes=[(op, model, str(id), fields, t0)])


class BulkChangeTrackerPolicy(BaseChangeTrackerPolicy):
    def __init__(self):
        super().__init__()
        self.changes: Dict[
            Tuple[str, str],
            Tuple[Literal["create", "delete", "update"], Optional[List[ChangeField]], float],
        ] = {}

    def register(
        self,
        op: Literal["create", "delete", "update"],
        model: str,
        id: str,
        fields: Optional[List[ChangeField]] = None,
    ) -> None:
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

        t0 = time.time()
        prev = self.changes.get((model, id))
        if prev is None:
            # First change
            self.changes[model, id] = (op, fields, t0)
            return
        # Series of change
        if op == "delete":
            # Delete overrides any operation
            self.changes[model, id] = (op, None, t0)
            return
        if op == "create":
            raise RuntimeError("create must be first update")
        # Update
        prev_op = prev[0]
        if prev_op == "create":
            # Create + Update -> Create with merged fields
            self.changes[model, id] = ("create", merge_fields(prev[1], fields), t0)
        elif prev_op == "update":
            # Update + Update -> Update with merged fields
            self.changes[model, id] = ("update", merge_fields(prev[1], fields), t0)
        elif prev_op == "delete":
            raise RuntimeError("Cannot update after delete")

    def commit(self) -> None:
        # Split to buckets
        changes = defaultdict(list)
        for (model_id, item_id), (op, fields, ts) in self.changes.items():
            part = 0
            changes[part].append((op, model_id, item_id, fields, ts))
        for part, items in changes.items():
            defer(CHANGE_HANDLER, key=part, changes=items)
