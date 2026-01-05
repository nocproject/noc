# ---------------------------------------------------------------------
# ObjectWatch model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Iterable, Tuple, Any

# Python modules
from noc.models import is_document
from .types import ObjectEffect, WatchItem

WATCHER_JCLS = "noc.services.scheduler.jobs.run_watchers.RunWatchersJob"
WAIT_DEFAULT_INTERVAL_SEC = 180
MIN_NEXT_SHIFT_SEC = 30


def get_next_ts(next_ts: Optional[datetime.datetime]):
    now = datetime.datetime.now().replace(microsecond=0)
    if not next_ts:
        next_ts = now + datetime.timedelta(seconds=WAIT_DEFAULT_INTERVAL_SEC)
    elif next_ts <= now:
        next_ts = now + datetime.timedelta(seconds=MIN_NEXT_SHIFT_SEC)
    return next_ts


def update_watchers(
    self,
    to_watchers: List[WatchItem],
    to_remove: Optional[List[Tuple[ObjectEffect, str, Optional[str]]]] = None,
    dry_run: bool = False,
    bulk=None,
):
    """Update watchers to disk"""
    self.update_object_watchers(to_watchers, to_remove, dry_run=dry_run, bulk=bulk)


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
    once: bool = True,
    after: Optional[datetime.datetime] = None,
    wait_avail: bool = False,
    remote_system: Optional[Any] = None,
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
        remote_system: From Remote System
    """
    # is_supported
    if effect not in self.supported_watcher_effects:
        raise ValueError("Not supported options")
    to_watchers = []
    # When save - skip maintenance
    for w in self.iter_watchers():
        if (
            effect == w.effect
            and key == w.key
            and (not remote_system or remote_system == w.remote_system)
        ):
            w.after = after
            w.args = kwargs
            to_watchers.append(w)
    if not to_watchers:
        to_watchers.append(
            WatchItem(
                effect=effect,
                key=str(key or ""),
                once=once,
                after=after,
                args=kwargs,  # Convert to string
                wait_avail=wait_avail,
                remote_system=remote_system.name if remote_system else None,
            )
        )
    if to_watchers:
        self.update_watchers(to_watchers)


def stop_watch(
    self, effect: ObjectEffect, key: Optional[str] = None, remote_system: Optional[Any] = None
):
    """Stop waiting callback"""
    to_remove = []
    for w in self.iter_watchers():
        if (
            w.effect == effect
            and w.key == key
            and (not remote_system or remote_system.name == w.remote_system)
        ):
            to_remove.append((w.effect, w.key, w.remote_system))
            continue
    if to_remove:
        self.update_watchers([], to_remove)


def touch_watch(
    self,
    effect: Optional[ObjectEffect] = None,
    is_avail: bool = False,
    dry_run: bool = True,
) -> List[WatchItem]:
    """
    Processed watchers
    Args:
        is_avail: Flag for object available status
        effect:
        dry_run: For tests run
    """
    now = datetime.datetime.now() + datetime.timedelta(seconds=10)  # time drift
    r, to_remove = [], []
    for w in self.iter_watchers():
        if effect and w.effect != effect:
            continue
        if w.wait_avail and not is_avail:
            continue
        if w.after and w.after > now:
            continue
        r.append(w)
        # After processed - Remove if once
        if w.once:
            to_remove.append((w.effect, w.key, w.remote_system))
    if to_remove and not dry_run:
        self.update_watchers([], to_remove)
    return r


# def update_watchers_bulk(
#     cls,
#     effect: ObjectEffect,
#     key: str,
#     ids,
#     once: bool = False,
#     after: Optional[datetime.datetime] = None,
# ):
#     """Bulk update watchers"""


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
    elif hasattr(cls, "update_object_watchers") and hasattr(cls, "iter_object_watchers"):
        # Django model
        cls.iter_watchers = iter_model_watchers
    else:
        return cls

    # cls.touch_watch = touch_watch
    cls.get_wait_ts = get_wait_ts
    cls.add_watch = add_watch
    cls.stop_watch = stop_watch
    cls.touch_watch = touch_watch
    cls.update_watchers = update_watchers

    return cls
