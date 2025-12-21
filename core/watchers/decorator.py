# ---------------------------------------------------------------------
# ObjectWatch model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
from typing import Optional, List, Iterable

# Python modules
from noc.models import is_document
from .types import ObjectEffect, WatchItem

watcher_logger = logging.getLogger(__name__)


def save_watchers(
    self,
    watchers: List[WatchItem],
    dry_run: bool = False,
    bulk=None,
    # changed_fields: Optional[List[ChangeField]] = None,
):
    """Save watchers to object"""
    # Add - insert_one
    # Stop - remove
    # Update after touch ?
    self.save_object_watchers(watchers, dry_run=dry_run, bulk=bulk)


def iter_model_watchers(self) -> Iterable["WatchItem"]:
    """Iterable watch"""
    yield from self.iter_object_watchers()


def iter_document_watchers(self) -> Iterable["WatchItem"]:
    """Iterable watch"""
    for w in self.watchers:
        yield w.item


def get_wait_ts(self, timestamp: Optional[datetime.datetime] = None):
    """Return near watch time"""
    wait_ts = []
    for w in self.iter_watchers():
        if w.after:
            wait_ts.append(w.after)
    if timestamp:
        wait_ts.append(timestamp)
    if wait_ts:
        return min(wait_ts)
    return None


def add_watch(
    self,
    effect: ObjectEffect,
    key: Optional[str] = None,
    once: bool = False,
    after: Optional[datetime.datetime] = None,
    wait_avail: bool = False,
    # action: Optional[ActionType] = None, # Reaction ?
    **kwargs,
):
    """
    Adding new watch to object
    Args:
        effect: Watched effect
        key: Effect key
        once: Run only once
        after: Run After Timer
        wait_avail: Only Available status
    """
    # is_supported
    # if not self.is_supported_watch(effect):
    if effect not in self.supported_watcher_effects:
        raise ValueError("Not supported options")
    new_watchers = []
    changed, is_new = False, True
    # When save - skip maintenance
    for w in self.iter_watchers():
        if effect == w.effect and key == w.key:
            w.after = after
            is_new = False
        new_watchers.append(w)
    if is_new:
        new_watchers.append(
            WatchItem(
                effect=effect,
                key=str(key),
                once=once,
                after=after,
                args=kwargs,  # Convert to string
                wait_avail=wait_avail,
            )
        )
        changed |= True
    if changed:
        self.save_watchers(new_watchers)


def stop_watch(self, effect: ObjectEffect, key: str):
    """Stop waiting callback"""
    new_watchers = []
    changed = False
    for w in self.iter_watchers():
        if w.effect == effect and w.key == key:
            changed |= True
            continue
        new_watchers.append(w)
    if changed:
        self.save_watchers(new_watchers)


def touch_watch(
    self,
    is_avail: bool = False,
    is_update: bool = False,
    dry_run: bool = False,
):
    """
    Processed watchers
    Args:
        is_avail: Flag for object available status
        is_update: Flag for refresh_alarm procedure
        dry_run: For tests run
    """
    now = datetime.datetime.now() + datetime.timedelta(seconds=10)  # time drift
    for w in self.iter_watchers():
        if w.once and is_update:
            continue
        if w.immediate:
            # If Immediate, not run (used for save run only)
            continue
        if w.after and w.after > now:
            continue
        try:
            w.run(self, dry_run=dry_run)
        except Exception as e:
            print(f"Exception when run Watch Action: {e}")


def update_watchers(
    cls,
    effect: ObjectEffect,
    key: str,
    ids,
    once: bool = False,
    after: Optional[datetime.datetime] = None,
):
    """Bulk update watchers"""


def watchers(cls):
    """
    @capabilities

    Methods contributed to class:
    * update_caps: Update object capabilities
    * set_caps: Set capabilities value
    * get_caps: Getting effective capabilities

    """

    # Register models
    if hasattr(cls, "SUPPORTED_EFFECTS"):
        cls.supported_watcher_effects = frozenset(cls.SUPPORTED_EFFECTS)
    else:
        cls.supported_watcher_effects = frozenset(
            [ObjectEffect.MAINTENANCE, ObjectEffect.WIPING, ObjectEffect.WF_EVENT],
        )
    if is_document(cls):
        # MongoEngine model
        cls.iter_watchers = iter_document_watchers
    elif hasattr(cls, "save_object_watchers") and hasattr(cls, "iter_object_watchers"):
        # Django model
        cls.iter_watchers = iter_model_watchers
    else:
        return cls

    # cls.touch_watch = touch_watch
    cls.get_wait_ts = get_wait_ts
    cls.add_watch = add_watch
    cls.stop_watch = stop_watch
    cls.save_watchers = save_watchers

    return cls
