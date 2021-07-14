# ----------------------------------------------------------------------
# Change tracking policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import contextlib
import time
from collections import defaultdict
from typing import Optional, Tuple, List, Dict
from abc import ABCMeta, abstractmethod


# NOC modules
from noc.core.defer import defer
from noc.core.hash import hash_int


CHANGE_HANDLER = "noc.core.change.change.on_change"


tls = threading.local()


class ChangeTracker(object):
    """
    Thread-local change tracker.
    """

    @staticmethod
    def get_policy() -> "BaseChangeTrackerPolicy":
        policy = getattr(tls, "_ct_policy", None)
        if not policy:
            policy = SimpleChangeTrackerPolicy()
            tls._ct_policy = policy
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
        prev_policy = getattr(tls, "_ct_policy", None)
        if prev_policy:
            # Something to store
            stack = getattr(tls, "_ct_policy_stack", None) or []
            stack.append(prev_policy)
            tls._ct_policy_stack = stack
        # Store current policy
        tls._ct_policy = policy

    @staticmethod
    def pop_policy() -> Optional["BaseChangeTrackerPolicy"]:
        """
        Pop current effective policy from stack and restore previous one
        :return: Current effective policy
        """
        # Get current policy
        policy = getattr(tls, "_ct_policy", None)
        stack = getattr(tls, "_ct_policy_stack", None)
        if stack:
            # Install previous policy
            prev_policy = stack.pop(-1)
            tls._ct_policy = prev_policy
            if not stack:
                del tls._ct_policy_stack
        return policy

    @contextlib.contextmanager
    def bulk_changes(self):
        """
        Apply all changes at once
        :return:
        """
        # Store current effective policy
        prev_policy = getattr(tls, "_ct_policy", None)
        # Install bulk change policy as
        policy = BulkChangeTrackerPolicy()
        tls._ct_policy = policy
        yield
        policy.commit()
        if prev_policy:
            tls._ct_policy = prev_policy
        else:
            del tls._ct_policy


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

    def register(self, op: str, model: str, id: str, fields: Optional[List] = None) -> None:
        key = hash_int(id)
        t0 = time.time()
        defer(CHANGE_HANDLER, key=key, changes=[(op, model, str(id), fields, t0)])


class BulkChangeTrackerPolicy(BaseChangeTrackerPolicy):
    def __init__(self):
        super().__init__()
        self.changes: Dict[Tuple[str, str], Tuple[str, Optional[List], Optional[float]]] = {}

    def register(self, op: str, model: str, id: str, fields: Optional[List] = None) -> None:
        def merge_fields(f1: Optional[List[str]], f2: Optional[List[str]]) -> Optional[List[str]]:
            f1 = f1 or []
            f2 = f2 or []
            return list(set(f1) | set(f2))

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
