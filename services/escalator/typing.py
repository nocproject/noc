# ---------------------------------------------------------------------
# Escalator job typing
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import enum


class ActionStatus(enum.Enum):
    """
    Action Result Status

    Attributes:
        NEW: new action
        SUCCESS: run success
        FAILED: Failed with error
        WARNING: Warning. Failed, but allowed to fail.
        SKIP: Not running about condition
        PENDING: Pending, waiting for manual approve.
        CANCELLED: Cancelled, not repeat for run / OR Condition
    """

    NEW = "n"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "w"
    # CANCELLED = "c"
    SKIP = "k"
    PENDING = "p"
    # WAIT_END = "we"
    # STOP = "stop/break"


class JobStatus(enum.Enum):
    """
    Job status.

    Attributes:
        PENDING: waiting for manual approve.
        NEXT:
        RUNNING:
        CANCEL: Job cancelled fot run
        WAIT: Waiting, ready to run.
        FAILED: End with fail
        WARNING: Failed, but allowed to fail.
        END: End job
        EXCEPTION: End for exception
    """

    PENDING = "p"  # Wait manual approve
    NEXT = "n"  # Next action
    WAIT = "w"  # Wait timestamp
    FAILED = "f"  # end with fail
    WARNING = "w"  # Retry errors
    CANCEL = "c"  # Manually cancelled
    END = "e"  # Run End
    EXCEPTION = "x"


class ItemStatus(enum.Enum):
    """
    Attributes:
        NEW: New items
        CHANGED: Items was changed
        FAIL: Failed when add to escalation
        EXISTS: Escalate over another doc
        REMOVED: Removed from escalation
    """

    NEW = "new"  # new item
    CHANGED = "changed"  # item changed
    FAIL = "fail"  # escalation fail
    EXISTS = "exists"  # Exists on another escalation
    REMOVED = "removed"  # item removed
