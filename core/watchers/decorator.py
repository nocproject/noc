# ---------------------------------------------------------------------
# ObjectWatch model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Iterable, Tuple

# Python modules
from noc.models import is_document, get_model_id
from .types import ObjectEffect, WatchItem

WATCHER_JCLS = "noc.services.scheduler.jobs.run_watchers.RunWatchersJob"
SCHEDULER = "scheduler"
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
    remote_system: Optional[str] = None,
    dry_run: bool = False,
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
    to_watchers, key = [], key or None
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
                key=key or None,
                once=once,
                after=after,
                args=kwargs,  # Convert to string
                wait_avail=wait_avail,
                remote_system=remote_system if remote_system else None,
            )
        )
    if to_watchers:
        self.update_watchers(to_watchers, dry_run=dry_run)


def stop_watch(
    self,
    effect: ObjectEffect,
    key: Optional[str] = None,
    remote_system: Optional[str] = None,
    stop_effect: bool = False,
    dry_run: bool = False,
):
    """Stop waiting callback"""
    to_remove = []
    for w in self.iter_watchers():
        if (
            w.effect == effect
            and (stop_effect or w.key == key)
            and (not remote_system or remote_system == w.remote_system)
        ):
            if w.remote_system:
                to_remove.append((w.effect, w.key, w.remote_system.name))
            else:
                to_remove.append((w.effect, w.key, w.remote_system))
            continue
    if to_remove:
        self.update_watchers([], to_remove, dry_run=dry_run)


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
        # Shift Runtime
    if to_remove and not dry_run:
        self.update_watchers([], to_remove, dry_run=dry_run)
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


def update_document_watchers(
    self,
    to_watchers: List[WatchItem],
    to_remove: Optional[List[Tuple[ObjectEffect, str, Optional[str]]]] = None,
    dry_run: bool = False,
    bulk=None,
):
    """"""
    from noc.core.scheduler.scheduler import Scheduler
    from noc.sa.models.objectwatchersitem import WatchDocumentItem

    updates = []
    up_w = {(w.effect, w.key, w.remote_system): w for w in to_watchers}
    for w in self.watchers:
        wi = w.item
        rs = w.remote_system.name if w.remote_system else None
        if to_remove and (wi.effect, wi.key, rs) in to_remove:
            continue
        update = up_w.pop((wi.effect, wi.key, rs), None)
        if update:
            w = WatchDocumentItem.from_item(update)
        updates.append(w)
    for wi in up_w.values():
        updates.append(WatchDocumentItem.from_item(wi, remote_system=wi.remote_system))
    self.watchers = updates
    wait_ts = self.get_wait_ts()
    if self.watcher_wait_ts != wait_ts:
        self.watcher_wait_ts = wait_ts
    m_ts = self.get_min_wait_ts()
    if dry_run:
        return
    if wait_ts and (not m_ts or wait_ts <= m_ts):
        scheduler = Scheduler(SCHEDULER)
        scheduler.submit(jcls=WATCHER_JCLS, key=get_model_id(self), ts=get_next_ts(wait_ts))
    if self._created:
        return
    set_op = {"watchers": self.watchers, "watcher_wait_ts": self.watcher_wait_ts}
    self.update(**set_op)


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
        cls.update_watchers = update_document_watchers
    elif hasattr(cls, "update_object_watchers") and hasattr(cls, "iter_object_watchers"):
        # Django model
        cls.iter_watchers = iter_model_watchers
        cls.update_watchers = update_watchers
    else:
        return cls

    # cls.touch_watch = touch_watch
    cls.get_wait_ts = get_wait_ts
    cls.add_watch = add_watch
    cls.stop_watch = stop_watch
    cls.touch_watch = touch_watch

    return cls
