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

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EnumField, StringField, BooleanField, DictField, DateTimeField


# Python modules
from noc.models import is_document
from .types import ObjectEffect, WatchItem
from noc.aaa.models.user import User

watcher_logger = logging.getLogger(__name__)


class WatchDocumentItem(EmbeddedDocument):
    """
    Attributes:
        effect: Watch Effect
        key: Id for action Instance
        once: Run only once
        args: Addition options for run
    """

    meta = {"strict": False, "auto_create_index": False}

    effect: ObjectEffect = EnumField(ObjectEffect, required=True)
    # Match, Array
    key = StringField(required=False)
    after = DateTimeField(required=False)
    once: bool = BooleanField(default=True)
    # action: ActionType = EnumField(ActionType, required=False)
    # Action
    args = DictField(default=dict)

    def __str__(self):
        return f"{self.effect}:{self.key}"

    @property
    def item(self) -> "WatchItem":
        """"""
        return WatchItem(
            effect=self.effect,
            key=self.key,
            after=self.after,
            once=self.once,
            args=self.args,
        )


def save_model_watchers(
    self,
    watchers: List[WatchItem],
    dry_run: bool = False,
    bulk=None,
    # changed_fields: Optional[List[ChangeField]] = None,
):
    """"""

    if after or self.wait_ts:
        self.wait_ts = self.get_wait_ts()


def save_document_watchers(
    self,
    watchers: List[WatchItem],
    dry_run: bool = False,
    bulk=None,
    # changed_fields: Optional[List[ChangeField]] = None,
):
    """"""
    new_watchers = []
    for w in watchers:
        new_watchers.append(
            WatchDocumentItem(
                effect=w.effect, key=w.key, after=w.after, once=w.once, args=w.args,
            )
        )
    # Not Gen Changed/Gen only flag
    self.watchers = new_watchers
    wait_ts = self.get_wait_ts()
    if self.wait_ts != wait_ts:
        self.wait_ts = wait_ts
    if dry_run or self._created:
        return
    set_op = {"watchers": self.watchers, "wait_ts": self.wait_ts}
    self.update(**set_op)


def iter_model_watchers(self) -> Iterable["WatchItem"]:
    """Iterable watch """
    for w in self.watchers_set():
        yield w.item


def iter_document_watchers(self) -> Iterable["WatchItem"]:
    """Iterable watch """
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
    key: str,
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
        if w.clear_only and not is_clear:
            # Watch alarm_clear
            continue
        if w.once and is_update:
            continue
        if w.immediate:
            # If Immediate, not run (used for save run only)
            continue
        if w.after and w.after > now:
            continue
        try:
            w.run(self, is_clear=is_clear, dry_run=dry_run)
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

    # cls.touch_watch = touch_watch
    cls.get_wait_ts = get_wait_ts
    cls.add_watch = add_watch
    cls.stop_watch = stop_watch
    # Register models
    cls.supported_watcher_effects = frozenset()

    if is_document(cls):
        # MongoEngine model
        cls.iter_watchers = iter_document_watchers
        if not hasattr(cls, "save_watchers"):
            cls.save_watchers = save_document_watchers

    else:
        # Django model
        cls.iter_watchers = iter_model_watchers
        if not hasattr(cls, "save_watchers"):
            cls.save_watchers = save_model_watchers

    return cls
