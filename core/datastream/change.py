# ----------------------------------------------------------------------
# DataStream change notification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import contextlib
from collections import defaultdict
from typing import Optional, Any, Tuple, Set, List

# NOC modules
from noc.core.defer import defer
from noc.core.datastream.loader import loader

tls = threading.local()


class ChangeTracker(object):
    """
    Thread-local datastream change tracker.
    """

    @staticmethod
    def get_policy() -> "BaseChangeTrackerPolicy":
        policy = getattr(tls, "_ct_policy", None)
        if not policy:
            policy = SimpleChangeTrackerPolicy()
            tls._ct_policy = policy
        return policy

    def register(self, changes: List[Tuple[str, Any]]) -> None:
        """
        Register datastream change
        :param changes: List of (datastream, object id)
        :return:
        """
        self.get_policy().register(changes)

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
        Apply all datastream changes at once
        :return:
        """
        # Store current effective policy
        prev_policy = getattr(tls, "_ct_policy", None)
        # Install bulk change policy as
        policy = BulkChangeTrackerPolicy()
        tls._ct_policy = policy
        yield
        policy.apply()
        if prev_policy:
            tls._ct_policy = prev_policy
        else:
            del tls._ct_policy


change_tracker = ChangeTracker()


class BaseChangeTrackerPolicy(object):
    """
    Base class for change tracker policies
    """

    def __init__(self):
        ...

    def register(self, changes: List[Tuple[str, Any]]) -> None:
        ...

    def apply(self):
        """
        Apply collected changes
        :return:
        """

    def apply_changes(self, changes: List[Tuple[str, Any]]):
        if changes:
            defer("noc.core.datastream.change.do_changes", changes=changes)


class DropChangeTrackerPolicy(BaseChangeTrackerPolicy):
    """
    Drop all changes
    """


class SimpleChangeTrackerPolicy(BaseChangeTrackerPolicy):
    """
    Simple policy, applies every registered change
    """

    def register(self, changes: List[Tuple[str, Any]]) -> None:
        self.apply_changes(changes)


class BulkChangeTrackerPolicy(BaseChangeTrackerPolicy):
    def __init__(self):
        super().__init__()
        self.changes: Set[Tuple[str, Any]] = set()

    def register(self, changes: List[Tuple[str, Any]]) -> None:
        self.changes.update(changes)

    def apply(self):
        self.apply_changes(list(self.changes))


def do_changes(changes):
    """
    Change calculation worker
    :param changes: List of datastream name, object id
    :return:
    """
    # Compact and organize datastreams
    datastreams = defaultdict(set)
    for ds_name, object_id in changes:
        datastreams[ds_name].add(object_id)
    # Apply batches
    for ds_name in datastreams:
        ds = loader[ds_name]
        if not ds:
            continue
        ds.bulk_update(sorted(datastreams[ds_name]))
