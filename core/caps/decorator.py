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


def iter_model_caps(
    self, scope: Optional[str] = None, effective_only: bool = False
) -> Iterable[CapsValue]:
    """"""
    from inv.models.capability import Capability

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
            scope=scope or "",
        )


def iter_document_caps(
    self, scope: Optional[str] = None, effective_only: bool = False
) -> Iterable[CapsValue]:
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


def save_document_caps(self, caps: List[CapsValue]):
    """"""
    from noc.inv.models.capsitem import CapsItem

    self.caps += [
        CapsItem(capability=c.capability, value=c.value, source=c.source, scope=c.scope or "")
        for c in caps
    ]
    self.objects.filter(id=self.id).update(caps=self.caps)


def save_model_caps(self, caps: List[CapsValue]):
    """"""
    self.caps = [
        {
            "capability": str(c.capability.id),
            "value": c.value,
            "source": c.source,
            "scope": c.scope or "",
        }
        for c in caps
    ]
    self.objects.filter(id=self.id).update(caps=self.caps)
    self.update_init()
    self._reset_caches(self.id, credential=True)


def get_caps(self, scope: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a dict of effective object capabilities
    """

    caps = {}
    for c in self.iter_caps(scope=scope, effective_only=not scope):
        caps[c.name] = c.value
    return caps


def set_caps(self, key: str, value: Any, source: str = "manual", scope: Optional[str] = "") -> None:
    from noc.inv.models.capability import Capability

    changed_caps: List[CapsValue] = []
    caps = Capability.get_by_name(key)
    if not caps:
        return
    value = caps.clean_value(value)
    source = InputSource(source)
    for item in self.iter_caps():
        if item.capability == caps:
            if not scope or item.scope == scope:
                changed_caps.append(item.set_value(value))
                break
    else:
        changed_caps.append(
            CapsValue(
                capability=caps,
                value=value,
                source=source,
                scope=scope or "",
            )
        )
    if changed_caps:
        self.save_caps(changed_caps)


def update_caps(
    self, caps: Dict[str, Any], source: str, scope: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing capabilities with a new ones.
    Args:
        self:
        caps: dict of caps name -> caps value
        source: Source name
        scope: Scope name
    """
    from noc.inv.models.capability import Capability

    o_label = f"{scope or ''}|{self.name}|{source}"
    source = InputSource(source)
    # Update existing capabilities
    new_caps: List[CapsValue] = []
    seen = set()
    changed = False
    for ci in self.iter_caps():
        ci: CapsValue
        seen.add(ci.name)
        if scope and scope != ci.scope:
            logger.debug(
                "[%s] Not changing capability %s: from other scope '%s'",
                o_label,
                ci.name,
                ci.scope,
            )
        elif ci.source == source:
            if ci.name in caps:
                if caps[ci.name] != ci.value:
                    logger.info(
                        "[%s] Changing capability %s: %s -> %s",
                        o_label,
                        ci.name,
                        ci.value,
                        caps[ci.name],
                    )
                    new_caps.append(ci.set_value(caps[ci.name]))
                    changed = True
            else:
                logger.info("[%s] Removing capability %s", o_label, ci.name)
                changed = True
                continue
        elif ci.name in caps:
            logger.info(
                "[%s] Not changing capability %s: Already set with source '%s'",
                o_label,
                ci.name,
                ci.scope,
            )
        new_caps += [ci]
    # Add new capabilities
    for cn in set(caps) - seen:
        c = Capability.get_by_name(cn)
        if not c:
            logger.info("[%s] Unknown capability %s, ignoring", o_label, cn)
            continue
        logger.info("[%s] Adding capability %s = %s", o_label, cn, caps[cn])
        new_caps.append(
            CapsValue(
                capability=c,
                value=caps[cn],
                source=source,
                scope=scope or "",
            )
        )
        changed = True

    if changed:
        logger.info("[%s] Saving changes", o_label)
        self.save_caps(new_caps)
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

    if is_document(cls):
        # MongoEngine model
        from mongoengine import signals as mongo_signals

        cls.iter_caps = iter_document_caps
        if not hasattr(cls, "save_caps"):
            cls.save_caps = save_document_caps

    else:
        # Django model
        from django.db.models import signals as django_signals

        cls.iter_caps = iter_model_caps
        if not hasattr(cls, "save_caps"):
            cls.save_caps = save_model_caps

    return cls
