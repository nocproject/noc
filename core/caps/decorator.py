# ----------------------------------------------------------------------
# @capabilities decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, List, Dict, Any, Iterable

# NOC modules
from noc.models import is_document
from noc.core.models.inputsources import InputSource
from .types import CapsValue

logger = logging.getLogger(__name__)


def iter_model_caps(self, scope: Optional[str] = None) -> Iterable[CapsValue]:
    """"""
    from noc.inv.models.capability import Capability

    for ci in self.caps or []:
        c = Capability.get_by_id(ci["capability"])
        if not c:
            logger.info("Removing unknown capability id %s", ci["capability"])
            continue
        cs = ci.get("scope", "")
        if scope and scope != cs:
            continue
        source = ci.get("source", "manual")
        value = ci.get("value")
        value = c.clean_value(value)
        yield CapsValue(
            capability=c,
            value=value,
            source=InputSource(source),
            scope=cs,
        )


def iter_document_caps(self, scope: Optional[str] = None) -> Iterable[CapsValue]:
    """"""
    for ci in self.caps or []:
        if scope and scope != ci.scope:
            continue
        cs = ci.source or "manual"
        cv = ci.value
        cv = ci.capability.clean_value(cv)
        yield CapsValue(
            capability=ci.capability,
            value=cv,
            source=InputSource(cs),
            scope=ci.scope,
        )


def save_document_caps(self, caps: List[CapsValue], dry_run: bool = False):
    """"""
    from noc.inv.models.capsitem import CapsItem

    self.caps = [
        CapsItem(capability=c.capability, value=c.value, source=c.source.value, scope=c.scope or "")
        for c in caps
    ]
    if dry_run:
        return
    self.update(caps=self.caps)


def save_model_caps(self, caps: List[CapsValue], dry_run: bool = False):
    """"""
    self.caps = [
        {
            "capability": str(c.capability.id),
            "value": c.value,
            "source": c.source.value,
            "scope": c.scope or "",
        }
        for c in caps
    ]
    if dry_run:
        return
    self.objects.filter(id=self.id).update(caps=self.caps)
    self.update_init()
    self._reset_caches(self.id, credential=True)


def get_caps(self, scope: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a dict of effective object capabilities
    """

    caps = {}
    for c in self.iter_caps(scope=scope):
        if c.name in caps and c.scope:
            continue
        caps[c.name] = c.value
    return caps


def set_caps(self, key: str, value: Any, source: str = "manual", scope: Optional[str] = "") -> None:
    from noc.inv.models.capability import Capability

    new_caps: List[CapsValue] = []
    caps = Capability.get_by_name(key)
    if not caps:
        return
    value = caps.clean_value(value)
    source = InputSource(source)
    changed = False
    for item in self.iter_caps():
        if item.capability == caps:
            if not scope or item.scope == scope:
                new_caps.append(item.set_value(value))
                changed |= True
                logger.info("Change capability value: %s -> %s", item, value)
                continue
        new_caps += [item]
    if not changed:
        new_caps += [
            CapsValue(
                capability=caps,
                value=value,
                source=source,
                scope=scope or "",
            )
        ]
        logger.info("Adding capability: %s", new_caps[-1])
    if new_caps:
        self.save_caps(new_caps)


def reset_caps(self, caps: Optional[str] = None, scope: Optional[str] = None):
    """
    Remove caps from object
    Args:
        self: Object
        caps: Caps Name
        scope: Scope name
    """
    new_caps = []
    changed = False
    for item in self.iter_caps():
        if scope and scope == item.scope:
            changed |= True
            logger.info("Removing capability by scope: %s", scope)
            continue
        if caps and caps == item.name:
            changed |= True
            logger.info("Removing capability by name: %s", caps)
            continue
        new_caps.append(item)
    if changed:
        self.save_caps(new_caps)


def update_caps(
    self, caps: Dict[str, Any], source: str, scope: Optional[str] = None, dry_run: bool = False
) -> Dict[str, Any]:
    """
    Update existing capabilities with a new ones.
    * if set scope - processed items over that scope
    * if not set scope - priority over if not set scope
    * For source in same scope - priority by default, Manual, Discovery
    Args:
        self:
        caps: dict of caps name -> caps value
        source: Source name
        scope: Scope name
        dry_run: Not save changes
    """
    from noc.inv.models.capability import Capability

    o_label = f"{scope or ''}|{self}|{source}"
    source = InputSource(source)
    # Update existing capabilities
    new_caps: List[CapsValue] = []
    seen = set()
    changed = False
    for ci in self.iter_caps():
        seen.add(ci.name)
        if scope and scope != ci.scope:
            # For Separate scope - skipping update (ETL)
            logger.debug(
                "[%s] Not changing capability %s: from other scope '%s'",
                o_label,
                ci.name,
                ci.scope,
            )
        elif ci.source == InputSource.MANUAL:
            # Manual Source set only for set_caps method
            logger.info(
                "[%s] Not changing capability %s: Already set with source '%s'",
                o_label,
                ci.name,
                ci.scope,
            )
        elif ci.name in caps:
            value = ci.capability.clean_value(caps[ci.name])
            if value != ci.value:
                logger.info(
                    "[%s] Changing capability %s: %s -> %s",
                    o_label,
                    ci.name,
                    ci.value,
                    caps[ci.name],
                )
                ci = ci.set_value(caps[ci.name])
                changed |= True
            else:
                logger.debug(
                    "[%s] Not changing capability %s: Already set with source '%s'",
                    o_label,
                    ci.name,
                    ci.scope,
                )
        elif ci.name not in caps and scope == ci.scope:
            logger.info("[%s] Removing capability %s", o_label, ci)
            changed |= True
            continue
        new_caps += [ci]
    # Add new capabilities
    for cn in set(caps) - seen:
        c = Capability.get_by_name(cn)
        if not c:
            logger.info("[%s] Unknown capability %s, ignoring", o_label, cn)
            continue
        value = c.clean_value(caps[cn])
        logger.info("[%s] Adding capability %s = %s", o_label, cn, value)
        new_caps.append(
            CapsValue(
                capability=c,
                value=value,
                source=source,
                scope=scope or "",
            )
        )
        changed |= True

    if changed:
        logger.info("[%s] Saving changes", o_label)
        self.save_caps(new_caps, dry_run=dry_run)
    # get_caps
    caps = {}
    for ci in new_caps:
        caps[ci.name] = ci.value
    return caps


def capabilities(cls):
    """
    @capabilities

    Methods contributed to class:
    * update_caps: Update object capabilities
    * set_caps: Set capabilities value
    * get_caps: Getting effective capabilities

    """

    cls.update_caps = update_caps
    cls.get_caps = get_caps
    cls.set_caps = set_caps
    cls.reset_caps = reset_caps

    if is_document(cls):
        # MongoEngine model
        cls.iter_caps = iter_document_caps
        if not hasattr(cls, "save_caps"):
            cls.save_caps = save_document_caps

    else:
        # Django model
        cls.iter_caps = iter_model_caps
        if not hasattr(cls, "save_caps"):
            cls.save_caps = save_model_caps

    return cls
